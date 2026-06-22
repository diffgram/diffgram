import testUser from '../../../fixtures/users.json';
import testLabels from '../../../fixtures/labels.json';

describe('Annotation Text Interface display', () => {
  context('Text Interface display', () => {
    before(() => {
      Cypress.Cookies.debug(true, { verbose: true });

      cy.loginByForm(testUser.email, testUser.password)
        .gotToProject(testUser.project_string_id)
        .createLabels(testLabels);

      // Upload the text file once before all tests in this context
      cy.upload_text_file(testUser.project_string_id);
    });

    beforeEach(() => {
      // Logout and login again before each test to have a clean state
      cy.logout();
      cy.loginByForm(testUser.email, testUser.password);
    });

    it('Creates text token instances', () => {
      cy.visit(`/projects/${testUser.project_string_id}`)
        .wait(3000);

      cy.get('[data-cy="token_1_line_1"]').should('be.visible')
        .realMouseDown().realMouseUp()
        .wait(500)
        .realType("1")
        .wait(500)
        .get('[data-cy="text_label_0"]').should('be.visible')
        .realType("{esc}")
        .get('[data-cy="token_3_line_2"]').should('be.visible')
        .realMouseDown().realMouseUp()
        .realType("2")
        .get('[data-cy="text_label_1"]').should('be.visible');
    });

    // ... continue with the rest of the tests
  });
});
