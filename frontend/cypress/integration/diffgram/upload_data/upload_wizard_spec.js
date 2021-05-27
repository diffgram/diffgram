import testUser from '../../../fixtures/users.json';
import testLabels from '../../../fixtures/labels.json';


describe('Upload Wizard Spec Tests', () => {

  context('Upload Wizard Main Features', () => {
    before(function () {
      Cypress.Cookies.debug(true, {verbose: true})
      Cypress.Cookies.defaults({
        preserve: ['session']
      })
      // login before all tests
      cy.loginByForm(testUser.email, testUser.password);
      cy.gotToProject(testUser.project_string_id);
      cy.createLabels(testLabels)
      cy.visit(`http://localhost:8085/studio/upload/${testUser.project_string_id}`);
    })

    context('It Uploads and Views an image with no labels', () => {
      it('Correctly uploads an image on the wizard', () => {
        cy.uploadAndViewSampleImage(testUser.project_string_id);
      })
    })
    context('It Can Copy an Instance', () => {
      it('Correctly opens the context menu on a Bounding Box', () => {

      })
    })

    context('It Can Paste an Instance', () => {
      it('Correctly opens the context menu on a Bounding Box', () => {
        cy.mousedowncanvas(150, 150);
        cy.wait(1000)
        cy.rightclickdowncanvas(150, 150);
        cy.wait(1000)
        cy.get('[data-cy=copy_instance]').click({force: true});
        cy.mousedowncanvas(10,10)
        cy.rightclickdowncanvas(380, 380);
        cy.get('[data-cy=paste_instance]').click({force: true});

      })
    })

    context('It Can Paste an Instance Multiple Times Without Duplicating', () => {
      it('Correctly opens the context menu on a Bounding Box', () => {

        cy.window().then(window => {
          cy.get('[data-cy=save_button]').click({force: true})
            .type('{ctrl+v}', {force: true})
            .wait(500)
            .type('{ctrl+v}',{force: true})
            .wait(500)
            .type('{ctrl+v}',{force: true})
            .wait(500)
            .type('{ctrl+v}', {force: true})
            .get('[data-cy=save_button]').click({force: true})
            .wait(7500).then(()=>{
              let instance_list = window.AnnotationCore.instance_list;
              for(let i = 0; i < instance_list.length; i++){
                // Validate that each instance id exists just once on the
                expect(instance_list.filter(inst => inst.id === instance_list[i].id).length).to.equal(1)
              }
          })


        });

      })
    })

    // context('It Can Delete an Instance', () => {
    //   it('Correctly opens the context menu on a Bounding Box', () => {
    //     cy.mousedowncanvas(90, 90);
    //     cy.wait(1000)
    //     cy.rightclickdowncanvas(90, 90);
    //     cy.wait(1000)
    //     cy.mousedowncanvas(10,10)
    //     cy.rightclickdowncanvas(100, 100);
    //     cy.get('[data-cy=delete_instance]').click({force: true});
    //
    //   })
    // })
    //
    // context('It Share an Instance', () => {
    //   it('Correctly opens the context menu on a Bounding Box', () => {
    //     cy.mousedowncanvas(90, 90);
    //     cy.wait(1000)
    //     cy.rightclickdowncanvas(90, 90);
    //     cy.wait(1000)
    //     cy.mousedowncanvas(10,10)
    //     cy.rightclickdowncanvas(100, 100);
    //     cy.intercept( `/api/project/*/share-link`).as('share_link')
    //     cy.get('[data-cy=share_instance]').click({force: true});;
    //     cy.get('[data-cy=share_instance_textarea]').click();
    //     cy.get('[data-cy=share_instance_textarea]').type('hello world');
    //     cy.get('[data-cy=share_instance_button]').click();
    //     cy.wait('@share_link').should(({request, response}) =>{
    //       expect(request.method).to.equal('POST')
    //       // it is a good practice to add assertion messages
    //       // as the 2nd argument to expect()
    //       expect(response.statusCode, 'response status').to.eq(200)
    //     })
    //
    //   })
    // })

  })

})
