"use strict";
const env = require("dotenv");

env.config();

module.exports = {
  NODE_ENV: '"production"',
  mail_gun: process.env.VUE_APP_MAILGUN
};
