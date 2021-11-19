import testUser from '../../../fixtures/users.json';

describe('tasks_detail_pagination', () => {

  context('tasks_detail_pagination', () => {
    before(function () {

      cy.createSampleTasksUsingBackend(10)

      Cypress.Cookies.debug(true, {verbose: true})
      Cypress.Cookies.defaults({
        preserve: ['session']
      })
      cy.loginByForm(testUser.email, testUser.password);
      
    })

    it('Views job', () => {

      cy.visit(`http://localhost:8085/job/list`);
      cy.get('[data-cy="view_button"]').first().click({force: true})
      cy.wait(3000)

    })

  })

})