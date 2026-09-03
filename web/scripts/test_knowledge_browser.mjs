import { chromium } from "playwright";

async function run() {
  const browser = await chromium.launch({ channel: "msedge", headless: true });
  const page = await browser.newPage();
  
  const consoleLogs = [];
  page.on("console", (msg) => consoleLogs.push(`[${msg.type()}] ${msg.text()}`));
  page.on("pageerror", (err) => consoleLogs.push(`[pageerror] ${err.toString()}`));

  console.log("Navigating to http://localhost:3782/knowledge?kb=audit_science_sqp_20260829...");
  await page.goto("http://localhost:3782/knowledge?kb=audit_science_sqp_20260829", { waitUntil: "networkidle", timeout: 30000 });

  await page.waitForTimeout(3000);

  const title = await page.title();
  const textContent = await page.evaluate(() => document.body.innerText);
  console.log("Page title:", title);
  console.log("Console logs count:", consoleLogs.length);
  if (consoleLogs.length > 0) {
    console.log("Console logs:\n" + consoleLogs.join("\n"));
  }
  console.log("Page text preview:\n" + textContent.slice(0, 500));

  await browser.close();
}

run().catch((err) => {
  console.error("Browser run error:", err);
  process.exit(1);
});
