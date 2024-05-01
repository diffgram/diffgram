import testUser from '../../../fixtures/users.json';
import testLabels from '../../../fixtures/labels.json';

// This describe block contains all the tests related to the File Info feature
describe('File Info', () => {

  // This context block contains tests that require the user to be logged in and on the project page
  context('File Info', () => {
    // This 'before' hook runs once before all tests in this context block
    before(function () {
      Cypress.Cookies.debug(true, {verbose: true})

      // Logging in the user before all tests
      cy.loginByForm(testUser.email, testUser.password)
        // Navigating to the project page
        .gotToProject(testUser.project_string_id)
        // Creating labels for the project
        .createLabels(testLabels)
        // Uploading and viewing a sample image
        .uploadAndViewSampleImage(testUser.project_string_id)

    })

    // This context block contains tests related to displaying file information
    context('It Displays The Annotated File information', () => {

      // This test checks if the file information is displayed on the toolbar buttons
      it('Displays File Information on Toolbar Buttons', () => {
        cy.get('[data-cy=more_button]').click({force: true}); // Clicking on the more button
        cy.get('[data-cy=show_file_information]').click({force: true}) // Clicking on the show file information button

      })


      // This test checks if the linked file and tasks are displayed on the toolbar buttons
      it('Displays Linked File & Tasks on Toolbar Buttons', () => {
        cy.intercept('api/v1/project/*/task/list').as('task_list') // Intercepting the API call to get the task list
        cy.get('[data-cy=more_button]').click({force: true}); // Clicking on the more button
        cy.get('[data-cy=show_linked_relations_file]').click({force: true}) // Clicking on the show linked relations file button

        cy.wait('@task_list').should(({request, response}) => { // Waiting for the API call to complete
          expect(request.method).to.equal('POST') // Checking if the request method is POST
          // Adding an assertion message to the response status code check
          expect(response.statusCode, 'response status').to.eq(200) // Checking if the response status code is 200
        })

      })

    })

  })

})

