import { loginByForm, gotToProject, createLabels, uploadAndViewSampleVideo } from './commands';

describe('Annotate Files Tests', () => {

  context('Test Video Annotation', () => {
    beforeEach(function () {
      Cypress.Cookies.debug(true, {verbose: true})
      // login before each test
      cy.loginByForm(testUser.email, testUser.password)
        .gotToProject(testUser.project_string_id)
        .createLabels(testLabels)
        .uploadAndViewSampleVideo(testUser.project_string_id);
    });

    context('It Can Draw Boxes And Keep buffer dict references', () => {
      it('Draws a box on Video', () => {
        const url = '/api/project/*/file/*/annotation/update';
        cy.route({
          method: 'POST',
          url,
          response: {},
          status: 200,
          delay: 500
        }).as('save_instances');

        cy.window().then(window => {
          cy.get('[data-cy="minimize-file-explorer-button"]').click({force: true})
            .select_label()
            .wait(3000)
            .mousedowncanvas(75, 75)
            .wait(500)

            .mouseupcanvas()
            .wait(1000)

            .mousedowncanvas(160, 160)
            .wait(500)
            .mouseupcanvas()
            .wait(1000)
            .get('[data-cy="save_button"]').click({force: true})
            .wait('@save_instances')
            .then(({request, response}) => {
              expect(request.method).to.equal('POST');
              expect(response.status).to.eq(200);
            });

          cy.window().then(window => {
            const instances = window.AnnotationCore.test_instance_list_and_list_in_buffer_by_ref();
            expect(instances).to.not.be.null;
            cy.task('logWindow', window);
          });
        });

      });

      // ... other tests

    });

  });

});
