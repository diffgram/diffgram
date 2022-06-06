// ***********************************************************
// This example support/index.js is processed and
// loaded automatically before your test files.
//
// This is a great place to put global configuration and
// behavior that modifies Cypress.
//
// You can change the location of this file or turn off
// automatically serving support files with the
// 'supportFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/configuration
// ***********************************************************



// Import commands.js using ES2015 syntax:
import './commands'
import testUser from '../fixtures/users.json'
// Alternatively you can use CommonJS syntax:
// require('./commands')
before(function() {
  // Steps which need to be executed before all tests
  // Check if test user exists, befor all tests. If it does not register the test user
  //cy.registerProTestUser();

  cy.request({
    method: 'GET',
    url: `localhost:8085/api/user/exists/${testUser.email}`,
    failOnStatusCode: false
  }).then((response) =>{
    if(response.body.found){
      return
    }
    else{
      cy.registerDataPlatformTestUser();
    }
  })

});
Cypress.on('uncaught:exception', (err, runnable) => {
  // returning false here prevents Cypress from
  // failing the test

  console.error(err)
  throw err
})

Cypress.on('fail', (err) => {

  throw err
});
