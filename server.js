// =========================
// Imports (must be first!)
// =========================
import express from "express";
import cors from "cors";
import path from "path";
import { fileURLToPath } from "url";

import { GoogleGenAI } from "@google/genai";


// =========================
// Setup __dirname in ES modules
// =========================
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// =========================
// YOUR ORIGINAL CODE (unchanged in logic)
// =========================
const ai = new GoogleGenAI({
  apiKey: "AIzaSyC7JoXjnEMZy-uKnvwsTfMdNfFI3qU4wB8",
});

async function main() {
  const response = await ai.models.generateContent({
    model: "gemini-2.5-pro",
    contents: "Explain how AI works in a few words",
  });

  console.log(response.text);
}

main();

// Prevent unhandled promise rejections from crashing the server.
// If Gemini fails on startup, we'll log it but KEEP RUNNING so Express can start.
process.on("unhandledRejection", (err) => {
  console.error("[Startup AI warmup failed]", err);
});

// =========================
// Helper to build prompt for interface generation
// =========================
function buildInterfacePrompt(userPrompt) {
  return `
You are an interface generator.

Goal:
Return a COMPLETE, SELF-CONTAINED mini app as pure HTML.
It must include <html>, <head>, <style>, <body>, and any <script> code needed.
All CSS and JS must be inline (no external CDN, no imports).
Do NOT include backticks.
Do NOT explain anything.
Output ONLY the code.

Behavior rules:
- Keep design modern, clean, rounded corners, subtle shadows.
- Use vanilla JS only (no React, no frameworks).
- Never use fetch to external URLs.
- The app must run fully offline inside an iframe with sandbox="allow-scripts allow-modals".

Example features you might build:
- notepad with save to localStorage
- todo list with add/remove
- calculator
- pomodoro timer
- drawing canvas with colors
- markdown editor with live preview
- etc.

Now generate the interface for this request:
"${userPrompt}"
`.trim();
}


// =========================
// Express app setup
// =========================
const app = express();

// Parse JSON bodies
app.use(express.json());

// CORS for everything, including file:// origins using preflight
app.use(cors());
app.options("*", cors());

// Serve static frontend (public/index.html, css, etc.)
// This lets you just go to http://localhost:3000/ in the browser.
app.use(express.static(path.join(__dirname, "public")));


// =========================
// Routes
// =========================

// Health check
app.get("/api/health", (req, res) => {
  res.json({
    ok: true,
    message: "Backend is running and ready.",
  });
});

// Generate interface route
app.post("/api/generate", async (req, res) => {
  try {
    // Basic validation
    const prompt = ((req.body && req.body.prompt) || "").trim();
    if (!prompt) {
      return res.status(400).json({
        success: false,
        error: "Missing prompt text.",
      });
    }

    // Build generation request for Gemini
    const generationRequest = buildInterfacePrompt(prompt);

    const aiResponse = await ai.models.generateContent({
      model: "gemini-2.5-flash",
      contents: generationRequest,
    });

    // Extract model text safely
    let generatedHtml = "";
    if (aiResponse) {
      if (typeof aiResponse.text === "function") {
        generatedHtml = aiResponse.text();
      } else if (typeof aiResponse.text === "string") {
        generatedHtml = aiResponse.text;
      } else if (
        aiResponse.response &&
        typeof aiResponse.response.text === "function"
      ) {
        generatedHtml = aiResponse.response.text();
      }
    }

    // Clean accidental ``` fences
    generatedHtml = (generatedHtml || "")
      .replace(/^\s*```(?:html)?/i, "")
      .replace(/```\s*$/, "")
      .trim();

    if (!generatedHtml) {
      return res.status(500).json({
        success: false,
        error: "Model did not return HTML.",
      });
    }

    return res.json({
      success: true,
      html: generatedHtml,
    });
  } catch (err) {
    console.error("Error in /api/generate:", err);

    return res.status(500).json({
      success: false,
      error:
        err && err.message
          ? err.message
          : "Unknown server error while generating interface.",
    });
  }
});

// =========================
// Start server
// =========================
const PORT = 3000;
app.listen(PORT, () => {
  console.log(`🔥 Server listening on http://localhost:${PORT}`);
  console.log(`➡ Open http://localhost:${PORT}/ in your browser`);
});
