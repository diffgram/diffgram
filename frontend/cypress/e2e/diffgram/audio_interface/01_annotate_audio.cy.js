import testUser from '../../../fixtures/users.json';
import testLabels from "../../../fixtures/labels.json";

describe('Annotation Audio Interface', () => {

    context('Audio Interface', () => {
        before(function () {
        Cypress.Cookies.debug(true, {verbose: true})

        // login before all tests
        cy.loginByForm(testUser.email, testUser.password)
          .gotToProject(testUser.project_string_id)
          .createLabels(testLabels)

        })

        it('Creates audio token instances', () => {
            cy.upload_audio_file(testUser.project_string_id);
            cy.wait(500)
            cy.get('[data-cy="waveform"]').should('be.visible')
        })
    })
})
