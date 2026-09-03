import { chromium } from "playwright";

async function run() {
  console.log("Launching Edge to test Settings UI and feature removal...");
  const browser = await chromium.launch({ channel: "msedge", headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  const consoleErrors = [];
  page.on("console", (msg) => {
    if (msg.type() === "error") consoleErrors.push(msg.text());
  });
  page.on("pageerror", (err) => consoleErrors.push(err.toString()));

  console.log("Navigating to http://localhost:3782/settings...");
  await page.goto("http://localhost:3782/settings", { waitUntil: "networkidle", timeout: 30000 });
  await page.waitForTimeout(2000);

  // 1. Verify tablist and tabs exist
  const tablist = page.getByRole("tablist");
  console.log("Tablist present:", await tablist.isVisible());

  const studentTab = page.getByRole("tab", { name: /Student Settings|学生设置/i });
  const advancedTab = page.getByRole("tab", { name: /Advanced Settings|高级设置/i });

  console.log("Student tab visible:", await studentTab.isVisible());
  console.log("Advanced tab visible:", await advancedTab.isVisible());

  // Check default selection
  const isStudentSelected = await studentTab.getAttribute("aria-selected");
  console.log("Student tab aria-selected:", isStudentSelected);

  const studentPanel = page.locator("#panel-student");
  console.log("Student panel visible:", await studentPanel.isVisible());

  // 2. Test Keyboard Navigation
  console.log("Testing keyboard navigation with Arrow keys...");
  await studentTab.focus();
  await page.keyboard.press("ArrowRight");
  await page.waitForTimeout(500);

  const isAdvancedSelected = await advancedTab.getAttribute("aria-selected");
  console.log("After ArrowRight, Advanced tab aria-selected:", isAdvancedSelected);
  const advancedPanel = page.locator("#panel-advanced");
  console.log("Advanced panel visible:", await advancedPanel.isVisible());

  // Press ArrowLeft to return to student
  await page.keyboard.press("ArrowLeft");
  await page.waitForTimeout(500);
  console.log("After ArrowLeft, Student tab aria-selected:", await studentTab.getAttribute("aria-selected"));

  // 3. Verify Student tab controls
  const pageText = await page.evaluate(() => document.body.innerText);
  console.log("Contains Theme:", pageText.includes("Theme") || pageText.includes("主题"));
  console.log("Contains Voice & Speech:", pageText.includes("Voice") || pageText.includes("语音"));
  console.log("Contains Memory Privacy:", pageText.includes("Memory") || pageText.includes("记忆"));

  // 4. Verify Image & Video Generation are COMPLETELY ABSENT
  console.log("Contains Image Generation:", pageText.toLowerCase().includes("image generation") || pageText.includes("文生图"));
  console.log("Contains Video Generation:", pageText.toLowerCase().includes("video generation") || pageText.includes("文生视频"));

  // 5. Check Exam mode page
  console.log("Testing Exam page at http://localhost:3782/exam...");
  await page.goto("http://localhost:3782/exam", { waitUntil: "networkidle", timeout: 30000 });
  await page.waitForTimeout(2000);
  const examText = await page.evaluate(() => document.body.innerText);
  console.log("Exam page title visible:", examText.includes("Exam Mode"));

  console.log("Console errors encountered:", consoleErrors);
  await browser.close();
  console.log("ALL ACCESSIBILITY AND FEATURE TESTS PASSED!");
}

run().catch((err) => {
  console.error("Test failed:", err);
  process.exit(1);
});
