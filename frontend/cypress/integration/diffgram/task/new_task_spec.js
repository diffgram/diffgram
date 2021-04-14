import testUser from '../../../fixtures/users.json'

// describe('New Task Template Creation', () => {
//   beforeEach (() => {
//     Cypress.Cookies.debug(true, {
//       names: ['session', 'csrftoken']
//     })
//   })
//
//   // Not quite sure on naming schemes here
//   context('Create new task template from list page', () => {
//     beforeEach(function () {
//       // login before each test
//       cy.loginByForm(testUser.email, testUser.password)
//     })
//
//     it('Creates new template', () => {
//
//       cy.visit('http://localhost:8085/job/list');
//       cy.wait(3000);
//
//       cy.get('[data-cy="new_tasks"]').click();
//       cy.wait(4000);
//
//       // TODO create label??? or?
//
//       cy.get('[data-cy="create-job-button"]').click();
//
//       cy.wait(3000);
//
//       // Select default dir
//       cy.get('[data-cy=directory_select]').first().click()
//       cy.get('.v-list.v-select-list div').contains(
//         'Default').click({force: true})
//
//       /// LEFT OFF HERE... this was the automated part from recorder
//       cy.get('.v-stepper__content:nth-child(4) > .v-stepper__wrapper').click();
//       cy.get('.v-stepper__wrapper > .v-btn').click();
//       cy.get('.pa-5:nth-child(7) > .v-btn__content').click();
//
//       cy.wait(9000);
//
//
//       cy.get('[data-cy=export-table]')
//         .find('[data-cy=export-row]')
//         .first()
//         .find('[data-cy=export-column]').find('[data-cy="download_export"]').first().click({force: true});
//     })
//
//   })
//
// })
