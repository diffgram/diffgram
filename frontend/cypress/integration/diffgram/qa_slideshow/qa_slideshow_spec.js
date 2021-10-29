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
    for (let i = 0; i < 3; i++) {
      cy.select_label("car");
      cy.mousedowncanvas(75, 75);
      cy.mouseupcanvas();
      cy.mousedowncanvas(120, 120);
      cy.mouseupcanvas();
      cy.wait(3000);
      cy.mousedowncanvas(90, 90);
      cy.mouseupcanvas();
    }
  });

  it("Tests if slideshow focuses on annotations correctly", () => {
    cy.get('[data-cy="open-annotation-show-menu"]').click();
    cy.wait(100);
    cy.get('[data-cy="start-annotation-show"]').click();
    cy.wait(3000);
    cy.get('[data-cy="show-progress-bar"]')
      .invoke("text")
      .then(initial_state => {
        cy.wait(1000);
        cy.get('[data-cy="show-progress-bar"]')
          .invoke("text")
          .then(finalS_state => {
            expect(initial_state).to.not.equal(finalS_state);
            cy.get('[data-cy="pause-annotation-show"]').click();
          });
      });
  });

  it("Tests if qa slideshow changes files correctly", () => {
    cy.location("search").then(loc => {
      cy.get('[data-cy="open-annotation-show-menu"]').click();
      cy.wait(100);
      cy.get('[data-cy="start-annotation-show"]').click();
      cy.wait(10000);
      cy.get('[data-cy="pause-annotation-show"]').click();
      cy.location("search").then(final => {
        expect(loc).to.not.equal(final);
      });
    });
  });
});
