// index.js
// ©2024, Ovais Quraishi
//
// TODO:
//	1. Use the reddit-llama API to post LLAMA response as replies to posts and comments
//		This method mimics real human interface.
//	2. Assume personas when posting
//		a. Persona who agrees with the original premise
//		b. Persona who disagress with the original premise 
//		c. Persona who rudely disagrees with the original premise
// LICENSE: The 3-Clause BSD License - license.txt

const { chromium } = require('playwright');
const loginModule = require('./modules/login');
const config = require('./config.json');

(async () => {
  const browser = await chromium.launch({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
	headless: false
  });
  const page = await browser.newPage();

  try {
    await loginModule.login(page, config.username, config.password);
    // Other tasks/modules can be invoked here
  } catch (error) {
    console.error('Error occurred:', error);
  } finally {
    await browser.close();
  }
})();

