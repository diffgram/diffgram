import testUser from '../../../fixtures/users.json';
import testLabels from "../../../fixtures/labels.json";

describe('Annotation Audio Interface', () => {

    context('Audio Interface', () => {
        before(function () {
        Cypress.Cookies.debug(true, {verbose: true})
        Cypress.Cookies.defaults({
            preserve: ['session']
        })
        // login before all tests
        cy.loginByForm(testUser.email, testUser.password);
        cy.gotToProject(testUser.project_string_id);
        cy.createLabels(testLabels)

        })

        it('Creates audio token instances', () => {
            cy.upload_audio_file(testUser.project_string_id);    
        })
    })
})
