import testUser from "../../../fixtures/users.json";
import testLabels from "../../../fixtures/labels.json";

describe("Test set for QA slideshow", () => {
  before(function() {
    Cypress.Cookies.debug(true, { verbose: true });
    Cypress.Cookies.defaults({
      preserve: ["session"]
    });
    // login before all tests
    cy.loginByForm(testUser.email, testUser.password);
    cy.gotToProject(testUser.project_string_id);
    cy.createLabels(testLabels);
    cy.uploadAndViewSampleImage(testUser.project_string_id);
  });

  it("If slideshow run correctly on tasks", () => {
    cy.get('[data-cy="navbar-logo"]').click();
    cy.wait(2000);
    cy.get("#open_main_menu").click();
    cy.get('[data-cy="main_menu_data_explorer"]').click();
    cy.wait(2000);
    cy.location("search").then(loc => {
      cy.get('[data-cy="open-annotation-show-menu"]').click();
      cy.wait(100);
      cy.get('[data-cy="start-annotation-show"]').click();
      cy.wait(5000);
      cy.get('[data-cy="pause-annotation-show"]').click();
      cy.location("search").then(final => {
        expect(loc).to.not.equal(final);
      });
    });
  });
});
