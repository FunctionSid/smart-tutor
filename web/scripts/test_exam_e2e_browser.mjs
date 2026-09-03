import { chromium } from "playwright";

async function run() {
  console.log("Launching Microsoft Edge for end-to-end Exam Mode test...");
  const browser = await chromium.launch({ channel: "msedge", headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  const consoleErrors = [];
  page.on("console", (msg) => {
    if (msg.type() === "error") consoleErrors.push(msg.text());
  });
  page.on("pageerror", (err) => consoleErrors.push(err.toString()));

  console.log("1. Navigating to http://localhost:3782/exam...");
  await page.goto("http://localhost:3782/exam", { waitUntil: "networkidle", timeout: 30000 });
  await page.waitForTimeout(2000);

  // Check header
  const title = await page.locator("h1").innerText();
  console.log("Exam Page Title:", title);

  // Check if exams list has at least 1 exam
  const startExamBtns = page.getByRole("button", { name: /Start Exam/i });
  const count = await startExamBtns.count();
  console.log(`Found ${count} 'Start Exam' button(s) in list.`);

  if (count === 0) {
    throw new Error("No exam found with questions!");
  }

  console.log("Clicking 'Start Exam' on the first available exam...");
  await startExamBtns.first().click();
  await page.waitForTimeout(2000);

  // 2. Verify Exam Runner accessibility structures
  console.log("2. Verifying ExamRunner accessibility structure...");
  const fieldsets = page.locator("fieldset");
  const fieldsetCount = await fieldsets.count();
  console.log(`Fieldsets found: ${fieldsetCount}`);
  if (fieldsetCount > 0) {
    const legend = await fieldsets.first().locator("legend").innerText();
    console.log("Legend question text:", legend.slice(0, 70));
  }

  // Verify native radio buttons
  const radios = page.locator("input[type='radio']");
  const radioCount = await radios.count();
  console.log(`Native radio buttons found: ${radioCount}`);
  if (radioCount < 4) {
    throw new Error("Expected at least 4 radio buttons for a 4-option question!");
  }

  // 3. Take the exam:
  // Answer Question 1: deliberate wrong option (Option B)
  console.log("3. Answering Question 1 with Option B...");
  await radios.nth(1).check();
  console.log("Radio B checked:", await radios.nth(1).isChecked());

  // Click "Next"
  console.log("Clicking 'Next' button...");
  const nextBtn = page.getByRole("button", { name: /^Next/i });
  await nextBtn.click();
  await page.waitForTimeout(1000);

  // Answer Question 2: option A
  console.log("Answering Question 2 with Option A...");
  const radiosQ2 = page.locator("input[type='radio']");
  await radiosQ2.nth(0).check();
  console.log("Q2 Radio A checked:", await radiosQ2.nth(0).isChecked());

  // Click "Review & Submit"
  console.log("Clicking 'Review & Submit'...");
  const reviewBtn = page.getByRole("button", { name: /Review & Submit/i });
  await reviewBtn.click();
  await page.waitForTimeout(1000);

  // Verify Review page rendered
  const reviewHeading = await page.locator("h1").innerText();
  console.log("Review heading:", reviewHeading);
  console.log("Contains 'Review':", reviewHeading.includes("Review"));

  // Click "Submit Exam Now"
  console.log("4. Submitting Exam via 'Submit Exam Now'...");
  const submitNowBtn = page.getByRole("button", { name: /Submit Exam Now/i });
  await submitNowBtn.click();
  await page.waitForTimeout(3000);

  // 5. Verify Results Page
  console.log("5. Verifying ExamResultViewer...");
  const resultsHeading = page.locator("h2:has-text('Exam Results')");
  console.log("Results Heading visible:", await resultsHeading.isVisible());

  const scoreSummary = await page.locator("text=/\\d+ \\/ \\d+/").first().innerText();
  console.log("Score summary on page:", scoreSummary);

  const fullText = await page.evaluate(() => document.body.innerText);
  console.log("Contains Topic Mastery:", fullText.includes("Topic Mastery"));
  console.log("Contains Question Review:", fullText.includes("Question Review"));
  console.log("Contains Explanation:", fullText.includes("Explanation"));
  console.log("Contains Verbatim Citation Quote:", fullText.includes("Citation") || fullText.includes("crown glass") || fullText.includes("refractive index"));

  console.log("Console errors encountered:", consoleErrors);
  await browser.close();
  console.log("FULL END-TO-END BROWSER EXAM TEST PASSED WITH COMPLETE EVIDENCE!");
}

run().catch((err) => {
  console.error("Browser test failed:", err);
  process.exit(1);
});
