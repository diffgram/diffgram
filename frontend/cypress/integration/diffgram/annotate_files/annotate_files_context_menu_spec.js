import testUser from '../../../fixtures/users.json';
import testLabels from '../../../fixtures/labels.json';


describe('Annotate Files Tests', () => {

  context('Test Annotate files Main Features', () => {
    before(function () {
      Cypress.Cookies.debug(true, {verbose: true})
      Cypress.Cookies.defaults({
        preserve: ['session']
      })
      // login before all tests
      cy.loginByForm(testUser.email, testUser.password);
      cy.gotToProject(testUser.project_string_id);
      cy.createLabels(testLabels)
      cy.uploadAndViewSampleImage(testUser.project_string_id);
      cy.wait(3000);
      // Minimize file explorer
      cy.get('[data-cy="minimize-file-explorer-button"]').click({force: true})
      // Select Label
      cy.get(`[data-cy="${testLabels[0].name}"]`).first().click({force: true})

      // Draw box
      cy.mousedowncanvas(75, 75);
      cy.wait(1500)

      cy.mouseupcanvas();
      cy.wait(1500)

      cy.mousedowncanvas(120, 120);
      cy.wait(1500)
      cy.mouseupcanvas();

      // Set Edit Mode False
      cy.get('[data-cy="edit_toggle"]').click({force: true})
    })

    context('It Has a Context Menu For Instance Specific Actions', () => {
      it('Correctly opens the context menu on a Bounding Box', () => {
        cy.mousedowncanvas(90, 90);
        cy.wait(1000)
        cy.mousedowncanvas(90, 90);
        cy.wait(1000)
        cy.rightclickdowncanvas(90, 90);
        cy.wait(1000)
        cy.get('[data-cy=copy_instance]').should('exist');
        cy.get('[data-cy=delete_instance]').should('exist');
      })
    })
    context('It Can Copy an Instance', () => {
      it('Correctly opens the context menu on a Bounding Box', () => {
        cy.mousedowncanvas(90, 90);
        cy.wait(1000)
        cy.rightclickdowncanvas(90, 90);
        cy.wait(1000)
        cy.get('[data-cy=copy_instance]').click({force: true});
        cy.mousedowncanvas(10,10)
        cy.rightclickdowncanvas(100, 100);
        cy.get('[data-cy=paste_instance]').should('exist');
      })
    })

    context('It Can Paste an Instance', () => {
      it('Correctly opens the context menu on a Bounding Box', () => {
        cy.mousedowncanvas(90, 90);
        cy.wait(1000)
        cy.rightclickdowncanvas(90, 90);
        cy.wait(1000)
        cy.get('[data-cy=copy_instance]').click({force: true});
        cy.mousedowncanvas(10,10)
        cy.rightclickdowncanvas(100, 100);
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
            .wait(2000).then(()=>{
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
