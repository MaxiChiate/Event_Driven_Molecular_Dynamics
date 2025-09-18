import fs from "fs";
import { createCanvas } from "canvas";
import readline from "readline";
import { spawn } from "child_process";
import { Command, InvalidArgumentError } from "commander";

const program = new Command();

program
  .name("particle-video")
  .description("Render particle simulation files into mp4 videos")
  .argument("<inputs>", "input simulation files")
  .requiredOption("-S, --board-size <number>", "side length of board", parsePositive)
  .requiredOption("-L, --idk-size <number>", "thingy length", parsePositive)
  // .requiredOption("--max-speed <number>", "set the simulation's max overall speed for proper particle color gradient")
  .option("--video-width <pixels>", "video width", parsePositiveInt, 500)
  .option("--video-height <pixels>", "video height", parsePositiveInt, 500)
  .option("--video-fps <int>", "frames per second", parsePositiveInt, 24)
  .option("--particle-ids", "add particle ids to each particle (mostly for debugging with few particles)");

async function main() {
  program.parse();
  const opts = program.opts();
  const input = program.args[0];

  const output =
    input
      .split("/")
      .at(-1)
      .replace(/\.\w+$/, "") + ".mp4";
  await generateVideo(input, output, opts);

  console.log(`Video saved as ${output}`);
}

main();

function writeFrame(stream, buffer) {
  return new Promise((resolve) => {
    if (!stream.write(buffer)) stream.once("drain", resolve);
    else resolve();
  });
}

async function generateVideo(inputPath, outputFile, opts) {
  const maxSpeed = await computeMaxSpeed(inputPath);
  const timestepIterator = parseTextStream(inputPath);

  const canvas = createCanvas(opts.videoWidth, opts.videoHeight);
  const ctx = canvas.getContext("2d");

  // --- Compute scaling and offsets ---
  const marginPx = 20;
  const availableSize = Math.min(opts.videoWidth, opts.videoHeight) - 2 * marginPx;
  const scale = availableSize / opts.boardSize;
  const offsetX = (opts.videoWidth - opts.boardSize * scale) / 3;
  const offsetY = (opts.videoHeight - opts.boardSize * scale) / 2;
  const mapX = (x) => offsetX + x * scale;
  const mapY = (y) => offsetY + y * scale;
  const mapR = (r) => r * scale;

  const ffmpeg = spawn("ffmpeg", [
    "-y",
    "-f",
    "rawvideo",
    "-pix_fmt",
    "rgba",
    "-s",
    `${opts.videoWidth}x${opts.videoHeight}`,
    "-r",
    String(opts.videoFps),
    "-i",
    "-",
    "-c:v",
    "libx264",
    "-crf",
    "20",
    "-preset",
    "fast",
    "-pix_fmt",
    "yuv420p",
    outputFile,
  ]);

  ffmpeg.stderr.on("data", (data) => {
    console.error("ffmpeg:", data.toString());
  });

  const dt = 1 / opts.videoFps;
  let collisionCount = 0;
  let isFirst = true;
  let currentTime = 0;
  for await (const [time, particles] of timestepIterator) {
    if (time < currentTime) {
      collisionCount++;
      continue;
    }
    // Real timestep frame — increment collision count here
    drawFrame(
      ctx,
      particles,
      opts.boardSize,
      opts.idkSize,
      scale,
      offsetX,
      offsetY,
      mapX,
      mapY,
      mapR,
      collisionCount,
      opts.particleIds,
      maxSpeed
    );
    if (!isFirst) {
      collisionCount++;
      isFirst = false;
    }
    const rgba = ctx.getImageData(0, 0, opts.videoWidth, opts.videoHeight).data;
    await writeFrame(ffmpeg.stdin, Buffer.from(rgba));
    currentTime += dt;
  }

  ffmpeg.stdin.end();
  await new Promise((resolve) => ffmpeg.on("close", resolve));
}

/**
 * Draws a frame on a canvas.
 * @param {CanvasRenderingContext2D} ctx - The 2D rendering context of a canvas.
 */
function drawFrame(
  ctx,
  particles,
  boardSize,
  L,
  scale,
  offsetX,
  offsetY,
  mapX,
  mapY,
  mapR,
  collisionCount = null,
  particleIds,
  maxSpeed
) {
  // Background
  ctx.fillStyle = "black";
  ctx.fillRect(0, 0, ctx.canvas.width, ctx.canvas.height);

  // Board bounds
  ctx.strokeStyle = "#FFFFFF";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(offsetX, offsetY);
  ctx.lineTo(offsetX + boardSize * scale, offsetY);
  ctx.lineTo(offsetX + boardSize * scale, offsetY + ((boardSize - L) / 2) * scale);
  ctx.lineTo(offsetX + 2 * boardSize * scale, offsetY + ((boardSize - L) / 2) * scale);
  ctx.lineTo(offsetX + 2 * boardSize * scale, offsetY + ((boardSize + L) / 2) * scale);
  ctx.lineTo(offsetX + boardSize * scale, offsetY + ((boardSize + L) / 2) * scale);
  ctx.lineTo(offsetX + boardSize * scale, offsetY + boardSize * scale);
  ctx.lineTo(offsetX, offsetY + boardSize * scale);
  ctx.lineTo(offsetX, offsetY);
  ctx.stroke();

  // Collision counter (if provided)
  if (collisionCount !== null) {
    ctx.fillStyle = "white";
    ctx.font = `20px sans-serif`;
    ctx.textAlign = "left";
    ctx.textBaseline = "top";
    ctx.fillText(`Collisions: ${collisionCount}`, 10, 10);
  }

  // Particles
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillStyle = "white";
  ctx.font = `${12 * scale}px sans-serif`; // scale font roughly with board

  particles.forEach((p, i) => {
    const cx = mapX(p.x);
    const cy = mapY(p.y);
    const r = mapR(p.r);
    const color = speedToColor(p.speed, maxSpeed);

    // Circle
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, 2 * Math.PI);
    ctx.fillStyle = color;
    ctx.fill();

    // Text (id)
    if (particleIds) {
      ctx.fillStyle = "black";
      const fontSize = Math.max(r * 1.5, 8); // at least 8px
      ctx.font = `${fontSize}px sans-serif`;
      ctx.fillText(String(i), cx, cy);
    }
  });
}

function speedToColor(v, maxSpeed) {
  // normalize [0,1]
  const norm = maxSpeed > 0 ? v / maxSpeed : 0;

  // map 0 → 240 (blue), 1 → 0 (red)
  const hue = 240 - norm * 240;

  return `hsl(${hue}, 100%, 50%)`;
}

async function* parseTextStream(path) {
  const fileStream = fs.createReadStream(path);
  const rl = readline.createInterface({ input: fileStream });

  let particles = [];
  let currentTime = null;

  for await (const line of rl) {
    const trimmed = line.trim();
    if (!trimmed) continue;

    if (/^\d+(\.\d+)?$/.test(trimmed)) {
      if (currentTime !== null) {
        yield [currentTime, particles];
        particles = [];
      }
      currentTime = parseFloat(trimmed);
    } else {
      const [x, y, vx, vy, r] = trimmed.split(",").map(Number);
      particles.push({ x, y, vx, vy, r, speed: Math.sqrt(vx ** 2 + vy ** 2) });
    }
  }

  if (currentTime !== null && particles.length) {
    yield [currentTime, particles];
  }
}

async function computeMaxSpeed(path) {
  console.log("Computing maxSpeed...");
  const fileStream = fs.createReadStream(path);
  const rl = readline.createInterface({
    input: fileStream,
    crlfDelay: Infinity,
  });

  let maxSpeed = 0;

  for await (const line of rl) {
    const trimmed = line.trim();
    if (trimmed.length === 0) continue;

    // Skip lines that are just the timestep (a single number)
    if (!trimmed.includes(",")) continue;

    // Parse particle line: x,y,vx,vy,radius
    const [x, y, vx, vy, r] = trimmed.split(",").map(Number);
    const speed = Math.sqrt(vx * vx + vy * vy);
    if (speed > maxSpeed) {
      maxSpeed = speed;
    }
  }

  console.log("maxSpeed: ", maxSpeed);
  return maxSpeed;
}

// ---------- helpers ----------
function parsePositive(value) {
  const num = Number(value);
  if (isNaN(num) || num <= 0) {
    throw new InvalidArgumentError("Must be a positive number");
  }
  return num;
}

function parsePositiveInt(value) {
  const num = parsePositive(value);
  if (!Number.isInteger(num)) {
    throw new InvalidArgumentError("Must be a positive integer");
  }
  return num;
}
