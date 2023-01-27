import testUser from '../../../fixtures/users.json';
import testLabels from '../../../fixtures/labels.json';


describe('File Info', () => {

  context('File Info', () => {
    before(function () {
      Cypress.Cookies.debug(true, {verbose: true})

      // login before all tests
      cy.loginByForm(testUser.email, testUser.password)
        .gotToProject(testUser.project_string_id)
        .createLabels(testLabels)
        .uploadAndViewSampleImage(testUser.project_string_id)

    })

    context('It Displays The Annotated File information', () => {

      it('Displays File Information on Toolbar Buttons', () => {
        cy.get('[data-cy=more_button]').click({force: true});
        cy.get('[data-cy=show_file_information]').click({force: true})

      })


      it('Displays Linked File & Tasks on Toolbar Buttons', () => {
        cy.intercept('api/v1/project/*/task/list').as('task_list')
        cy.get('[data-cy=more_button]').click({force: true});
        cy.get('[data-cy=show_linked_relations_file]').click({force: true})

        cy.wait('@task_list').should(({request, response}) => {
          expect(request.method).to.equal('POST')
          // it is a good practice to add assertion messages
          // as the 2nd argument to expect()
          expect(response.statusCode, 'response status').to.eq(200)
        })

      })

    })

  })

})
