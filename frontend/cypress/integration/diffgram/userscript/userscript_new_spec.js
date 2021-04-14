import testUser from '../../../fixtures/users.json';
import testLabels from "../../../fixtures/labels.json";


describe('UserScript New', () => {

  context('Setup Image', () => {
    before(function () {
      Cypress.Cookies.debug(true, {verbose: true})
      Cypress.Cookies.defaults({
        preserve: ['session']
      })
      // login before all tests
      cy.loginByForm(testUser.email, testUser.password);
      cy.gotToProject(testUser.project_string_id);
      cy.createLabels(testLabels)
      cy.visit(`http://localhost:8085/studio/annotate/${testUser.project_string_id}`)

      cy.uploadAndViewSampleImage(testUser.project_string_id);

    })

    context('Clicking New Button', () => {
      it('Clicking New Button', () => {

        cy.get('[data-cy="userscript_new"]').click({force: true})
        cy.wait(1000)

        let code_to_write = "diffgram.create_box(1,1,100,100)"

        cy.get('.CodeMirror textarea')
        // we use `force: true` below because the textarea is hidden
        // and by default Cypress won't interact with hidden elements
        .type(code_to_write, { force: true })
        .wait(1000)
        .get('[data-cy="userscript_run"]').click({force: true})
        .window().then(window => {
          expect(window.AnnotationCore.instance_list.length).to.equal(1);
          expect(window.AnnotationCore.instance_list[0].x_min).to.equal(1);
          expect(window.AnnotationCore.instance_list[0].y_min).to.equal(1);
          expect(window.AnnotationCore.instance_list[0].x_max).to.equal(100);
          expect(window.AnnotationCore.instance_list[0].y_max).to.equal(100);
        })
      })
     })
  })

})
