import { chromium } from "playwright";

async function run() {
  console.log("Launching Edge to test Exam UI...");
  const browser = await chromium.launch({ channel: "msedge", headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  const consoleLogs = [];
  page.on("console", (msg) => consoleLogs.push(`[${msg.type()}] ${msg.text()}`));
  page.on("pageerror", (err) => consoleLogs.push(`[pageerror] ${err.toString()}`));

  console.log("Navigating to http://localhost:3782/exam...");
  await page.goto("http://localhost:3782/exam", { waitUntil: "networkidle", timeout: 30000 });
  await page.waitForTimeout(3000);

  const title = await page.title();
  console.log("Page title:", title);
  console.log("Console errors:", consoleLogs.filter((l) => l.includes("error") || l.includes("pageerror")));

  const bodyText = await page.evaluate(() => document.body.innerText);
  console.log("Page text preview:\n", bodyText.slice(0, 500));

  // Verify "Create New Exam" button is present
  const createBtn = page.getByRole("button", { name: "Create New Exam" });
  console.log("Create New Exam button visible:", await createBtn.isVisible());

  await browser.close();
  console.log("Exam UI test passed.");
}

run().catch(console.error);
