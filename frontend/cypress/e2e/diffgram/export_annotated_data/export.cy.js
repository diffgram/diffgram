import testUser from '../../../fixtures/users.json'
describe('Export to Cloud Provider', () => {
  beforeEach (() => {
    Cypress.Cookies.debug(true, {
      names: ['session', 'csrftoken']
    })
  })

  context('Export files to connections', () => {
    beforeEach(function () {
      // login before each test
      cy.loginByForm(testUser.email, testUser.password)
      cy.gotToProject(testUser.project_string_id);
    })

    it('Correctly sends a Job export to AWS Connection', () => {

      cy.get('#open_main_menu').click();
      cy.get('#export_section').click();
      cy.wait(4000);
      cy.get('[data-cy=complete-files-only-checkbox]').click({force: true})
      cy.get('[data-cy=generate-export]').click()

      cy.wait(9000);
      cy.get('[data-cy=export-table]')
        .find('[data-cy=export-row]')
        .first()
        .find('[data-cy=export-column]').find('[data-cy="download_export"]').first().click({force: true});
    })

  })

})
