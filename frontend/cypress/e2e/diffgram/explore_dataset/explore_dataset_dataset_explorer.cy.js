// Import required fixtures for test users and labels
import testUser from '../../../fixtures/users.json';
import testLabels from '../../../fixtures/labels.json';

describe('Annotate Files Tests', () => {
  // Context for exploring the dataset
  context('Explore Dataset', () => {
    // Set up the environment before all tests in this context
    before(function () {
      Cypress.Cookies.debug(true, {verbose: true})

      // Login before all tests
      cy.loginByForm(testUser.email, testUser.password)
        .gotToProject(testUser.project_string_id)
        .createLabels(testLabels)
        .uploadAndViewSampleImage(testUser.project_string_id);
    });

    // Context for writing a query and filtering files
    context('It Can write a query and filter files', () => {
      // Test for correctly opening the context menu on a Bounding Box
      it('Correctly opens the context menu on a Bounding Box', () => {
        // Wait for 4 seconds
        cy.wait(4000);

        // Minimize the file explorer
        cy.get('[data-cy="minimize-file-explorer-button"]').click({force: true});
        cy.wait(1000);

        // Select the 'apple' label
        cy.select_label('apple');
        cy.wait(3000);

        // Define the bounding boxes to create
        const boxes = [[75,75,120,120], [95,95,180,180], [150,150,215,215]];

        // Create the bounding boxes
        for(const box of boxes){
          cy.mousedowncanvas(box[0], box[1]);
          cy.wait(500);
          cy.mouseupcanvas();
          cy.wait(1000);
          cy.mousedowncanvas(box[2], box[3]);
          cy.wait(500);
          cy.mouseupcanvas();
          cy.wait(2000);
        }

        // Open the file explorer
        cy.get('[data-cy="file_explorer_button"]').click({force: true});

        // Click on the 'Dataset Explorer' tab
        cy.get('[data-cy="tab__Dataset Explorer"]').click({force: true});

        // Open the advanced query settings
        cy.get('[data-cy="advanced-query-settings"]').click({force: true});
        cy.wait(500);

        // Clear the query input field
        cy.get('[data-cy=query_input_field]').clear();
        cy.wait(500);

        // Type the query to filter files
        cy.get('[data-cy=query_input_field]').clear().type('labels.apple > 1 {enter}');
        cy.wait(500);

        // Blur the query input field
        cy.get('[data-cy=query_input_field]').blur();
        cy.wait(1000);

        // Focus on the query input field again
        cy.get('[data-cy=query_input_field]').focus();

        // Wait for 2.5 seconds
        cy.wait(2500);

        // Check if there is at least one file preview
        cy.get('.file-preview').its('length').should('be.gte', 1);
      });
    });
  });
});
