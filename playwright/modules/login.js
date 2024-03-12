// modules/login.js
// ©2024, Ovais Quraishi
async function login(page, username, password) {
  await page.goto('https://www.reddit.com/');
  await page.waitForSelector('a[href*="/login"]');
  await page.click('a[href*="/login"]');
  await page.waitForSelector('#login > faceplate-tabpanel > auth-flow-modal:nth-child(1) > div.w-100 > faceplate-tracker > button');
  await page.waitForSelector('input[name="username"]');
  await page.type('input[name="username"]', username);
  await page.type('input[name="password"]', password);
  await page.click('#login > faceplate-tabpanel > auth-flow-modal:nth-child(1) > div.w-100 > faceplate-tracker > button');

  await page.waitForNavigation();
}

module.exports = {
  login,
};

