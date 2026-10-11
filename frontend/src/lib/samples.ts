/** Tiny generated photos used only as upload inputs. They are not evaluation results. */

function pngFile(name: string, draw: (ctx: CanvasRenderingContext2D) => void) {
  const canvas = document.createElement("canvas");
  canvas.width = 96;
  canvas.height = 72;
  const ctx = canvas.getContext("2d");
  if (!ctx) throw new Error("Canvas is not available.");
  draw(ctx);
  const url = canvas.toDataURL("image/png");
  return fetch(url)
    .then((response) => response.blob())
    .then((blob) => new File([blob], name, { type: "image/png" }));
}

export const sampleMakers = [
  {
    label: "Sky",
    make: () =>
      pngFile("sample-sky.png", (ctx) => {
        ctx.fillStyle = "#93c5fd";
        ctx.fillRect(0, 0, 96, 72);
        ctx.fillStyle = "#ffffff";
        ctx.fillRect(18, 16, 28, 14);
        ctx.fillRect(48, 28, 22, 12);
      }),
  },
  {
    label: "Leaf",
    make: () =>
      pngFile("sample-leaf.png", (ctx) => {
        ctx.fillStyle = "#d1fae5";
        ctx.fillRect(0, 0, 96, 72);
        ctx.fillStyle = "#059669";
        ctx.beginPath();
        ctx.ellipse(48, 36, 22, 14, -0.4, 0, Math.PI * 2);
        ctx.fill();
      }),
  },
  {
    label: "Paper",
    make: () =>
      pngFile("sample-paper.png", (ctx) => {
        ctx.fillStyle = "#e2e8f0";
        ctx.fillRect(0, 0, 96, 72);
        ctx.fillStyle = "#ffffff";
        ctx.fillRect(22, 10, 52, 52);
        ctx.fillStyle = "#94a3b8";
        ctx.fillRect(30, 22, 36, 3);
        ctx.fillRect(30, 30, 28, 3);
      }),
  },
];
