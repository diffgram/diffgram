import testUser from '../../../fixtures/users.json';
import labelsForAttributes from '../../../fixtures/labelsForAttributes.json';


describe('Annotate Files Tests', () => {

  context('Test Annotate Files Attributes Feature', () => {
    before(function () {
      Cypress.Cookies.debug(true, {verbose: true})

      // login before all tests
      cy.loginByForm(testUser.email, testUser.password)
        .gotToProject(testUser.project_string_id)
        .createLabels(labelsForAttributes)
        .uploadAndViewSampleImage(testUser.project_string_id)
        .goToSchemaFromToolbar()

    })
    const next_wizard_step = '[data-cy=wizard_navigation_next]'
    const wizard_step_container =  (step) => {return `[data-cy=attribute_wizard_step_${step}]`};
    const selectAttribute = labelsForAttributes[0].attributes.filter(attr => attr.type === 'select')[0];

    context('[Select} It Creates And Sets Value of Select Type', () => {

       it('Required label for test should exist', () => {
         cy.get(`[data-cy='${labelsForAttributes[0].name}']`).should('exist')
       })

       it('Creates Select Attribute', () => {

         cy.createAndSelectNewAttributeGroup()

         cy.get('[data-cy=attribute_kind_select]').click({force: true});
         cy.get('.v-list.v-select-list div').contains('Select').click({force: true})

       })

      it('Names Select Attribute', () => {
        cy.get(`${wizard_step_container(1)} ${next_wizard_step}`).click({force: true})

        cy.typesAttributePrompt(selectAttribute.prompt)
      })

      it('Attaches Attributes to Label', () => {
         cy.get(`${wizard_step_container(2)} ${next_wizard_step}`).click({force: true})
         cy.selectLabel(labelsForAttributes[0].name)
      })

      it('Choses Global VS Local Attribute', () => {
        cy.get(`${wizard_step_container(3)} ${next_wizard_step}`).click({force: true})

      })

      it('Creates new options for Attributes', () => {

         cy.get(`${wizard_step_container(4)} ${next_wizard_step}`).click({force: true})
         cy.createAttributeOptions(selectAttribute.options)

       })

       it('Sets the value for the select attribute in the studio', () =>{
         cy.wait(3000);
         const selectAttribute = labelsForAttributes[0].attributes.filter(attr => attr.type === 'select')[0];

         cy.goToStudioFromToolbar()

         cy.select_label('car with Attributes');

         // Draw a box
         cy.mousedowncanvas(75, 75);
         cy.mouseupcanvas();
         cy.mousedowncanvas(120, 120);
         cy.mouseupcanvas();
         cy.wait(3000);
         cy.mousedowncanvas(90, 90);
         cy.mouseupcanvas();
         // Select The Attribute
         cy.get(`[data-cy="attribute_group_header_${selectAttribute.prompt}"]`).first().click({force: true});
         cy.get(`[data-cy="${selectAttribute.prompt}_value_select"]`).first().click({force: true})
         cy.wait(1000)
         cy.get('.v-menu__content .v-list.v-select-list div').contains(selectAttribute.options[2]).first().click({force: true})
         // Save The attribute
         cy.intercept(`api/project/*/file/*/annotation/update`).as('annotation_update')
         cy.get('body').type('{esc}');

         cy.get('[data-cy="save_button"]').click({force: true})
         cy.wait('@annotation_update')
           .should(({request, response}) => {
             expect(request.method).to.equal('POST')
             // it is a good practice to add assertion messages
             // as the 2nd argument to expect()
             expect(response.statusCode, 'response status').to.eq(200)
           })
       })

     })

    context('[Free Text] It Creates And Sets Value of Free Text Type', () => {

      const selectAttribute = labelsForAttributes[0].attributes.filter(attr => attr.type === 'text')[0];

      it('Creates Free Text Attribute', () => {

        cy.goToSchemaFromToolbar()

        cy.createAndSelectNewAttributeGroup()

        cy.get('[data-cy=attribute_kind_select]').click({force: true});
        cy.get('.v-list.v-select-list div').contains('Free Text').click({force: true})
      })

      it('Names Free Text Attribute', () => {
        cy.get(`${wizard_step_container(1)} ${next_wizard_step}`).click({force: true})
        cy.typesAttributePrompt(selectAttribute.prompt)

      })

      it('Attaches Free Text Attributes to Labels', () => {

        cy.get(`${wizard_step_container(2)} ${next_wizard_step}`).click({force: true})
        cy.selectLabel(labelsForAttributes[0].name)

        cy.get(`${wizard_step_container(3)} ${next_wizard_step}`).click({force: true})
        cy.get(`${wizard_step_container(4)} ${next_wizard_step}`).click({force: true})
      })

      it('Sets the value for the free text attribute in the studio', () =>{
        cy.wait(3000);
        const selectAttribute = labelsForAttributes[0].attributes.filter(attr => attr.type === 'text')[0];

        cy.goToStudioFromToolbar()

        cy.select_label('car with Attributes');
        // Draw a box
        cy.mousedowncanvas(75, 75);
        cy.mouseupcanvas();
        cy.mousedowncanvas(120, 120);
        cy.mouseupcanvas();
        cy.wait(3000);
        cy.mousedowncanvas(110, 110);
        cy.mouseupcanvas();
        cy.get('[data-cy="save_button"]').click({force: true})
        // Select The Attribute
        cy.mousedowncanvas(110, 110);
        cy.mouseupcanvas();
        cy.get(`[data-cy="attribute_group_header_${selectAttribute.prompt}"]`).first().click({force: true});
        cy.get(`[data-cy="${selectAttribute.prompt}_value_textfield"]`).first().click({force: true})
        cy.get(`[data-cy="${selectAttribute.prompt}_value_textfield"]`).first().type('sample text attribute value')
        // Save The attribute
        cy.intercept(`api/project/*/file/*/annotation/update`).as('annotation_update')
        cy.get('body').type('{esc}');

        cy.get('[data-cy="save_button"]').click({force: true})
        cy.wait('@annotation_update')
          .should(({request, response}) => {
            expect(request.method).to.equal('POST')
            // it is a good practice to add assertion messages
            // as the 2nd argument to expect()
            expect(response.statusCode, 'response status').to.eq(200)
          })
      })

    })

    context('[Multiple Select] Creates And Sets Value of Multiple Select Type', () => {

      const multipleSelectAttribute = labelsForAttributes[0].attributes.filter(
          attr => attr.type === 'multiple_select')[0];

      it('Creates Multiple Select Attribute', () => {

         cy.goToSchemaFromToolbar()

         cy.createAndSelectNewAttributeGroup()

         cy.get('[data-cy=attribute_kind_select]').click({force: true});

         cy.get('.v-list.v-select-list div').contains('Multiple Select').click({force: true})

       })

      it('Names Select Attribute', () => {
        cy.get(`${wizard_step_container(1)} ${next_wizard_step}`).click({force: true})

        cy.typesAttributePrompt(multipleSelectAttribute.prompt)
      })

      it('[Multiple Select] Attaches Attributes to Label', () => {
         cy.get(`${wizard_step_container(2)} ${next_wizard_step}`).click({force: true})
         cy.selectLabel(labelsForAttributes[0].name)
      })


      it('[Multiple Select] Creates Options ', () => {
        cy.createAttributeOptions(multipleSelectAttribute.options)

        cy.get(`${wizard_step_container(4)} ${next_wizard_step}`).click({force: true})

      })

      it('Sets the value for the multiple select attribute in the studio', () =>{

        cy.goToStudioFromToolbar()

        cy.select_label('car with Attributes');

        // Draw a box
        cy.mousedowncanvas(75, 75);
        cy.mouseupcanvas();
        cy.mousedowncanvas(120, 120);
        cy.mouseupcanvas();
        cy.wait(3000);
        cy.mousedowncanvas(90, 90);
        cy.mouseupcanvas();
        // Select The Attribute
        cy.get(`[data-cy="attribute_group_header_${multipleSelectAttribute.prompt}"]`).first().click({force: true});
        cy.get(`[data-cy="${multipleSelectAttribute.prompt}_value_multiple_select"]`).click({force: true});
        cy.get('.v-menu__content .v-list.v-select-list div').contains(multipleSelectAttribute.options[0]).first().click({force: true})
        // Save The attribute
        cy.intercept(`api/project/*/file/*/annotation/update`).as('annotation_update')
        cy.get('body').type('{esc}');

        cy.get('[data-cy="save_button"]').click({force: true})
        cy.wait('@annotation_update')
          .should(({request, response}) => {
            expect(request.method).to.equal('POST')
            // it is a good practice to add assertion messages
            // as the 2nd argument to expect()
            expect(response.statusCode, 'response status').to.eq(200)
          })
      })

    })

    context('[Radio Button] Creates', () => {

      const selectAttribute = labelsForAttributes[1].attributes.filter(attr => attr.type === 'radio')[0];

      it('[Radio Button] Creates Attribute', () => {

         cy.goToSchemaFromToolbar()

         cy.createAndSelectNewAttributeGroup()

         cy.get('[data-cy=attribute_kind_select]').click({force: true});

         cy.get('.v-list.v-select-list div').contains('Radio').click({force: true})

       })

      it('[Radio Button] Names', () => {
        cy.get(`${wizard_step_container(1)} ${next_wizard_step}`).click({force: true})

        cy.typesAttributePrompt(selectAttribute.prompt)
      })

      it('[Radio Button] Attaches Attributes to Label', () => {
          cy.get(`${wizard_step_container(2)} ${next_wizard_step}`).click({force: true})
          cy.selectLabel(labelsForAttributes[0].name)
      })


      it('[Radio Button] Creates Options ', () => {
        cy.createAttributeOptions(selectAttribute.options)

        cy.get(`${wizard_step_container(4)} ${next_wizard_step}`).click({force: true})

      })


      it('Sets the value for the radio button attribute in the studio', () =>{
        cy.wait(3000);
        const selectAttribute = labelsForAttributes[1].attributes.filter(attr => attr.type === 'radio')[0];

        cy.goToStudioFromToolbar()

        cy.select_label('car with Attributes');

        // Draw a box
        cy.mousedowncanvas(75, 75);
        cy.mouseupcanvas();
        cy.mousedowncanvas(120, 120);
        cy.mouseupcanvas();
        cy.wait(3000);
        cy.mousedowncanvas(90, 90);
        cy.mouseupcanvas();
        // Select The Attribute
        cy.get(`[data-cy="attribute_group_header_${selectAttribute.prompt}"]`).first().click({force: true});
        cy.get(`[data-cy="${selectAttribute.prompt}_radio_${selectAttribute.options[2]}"]`).first().click({force: true})
        // Save The attribute
        cy.intercept(`api/project/*/file/*/annotation/update`).as('annotation_update')
        cy.get('body').type('{esc}');

        cy.get('[data-cy="save_button"]').click({force: true})
        cy.wait('@annotation_update')
          .should(({request, response}) => {
            expect(request.method).to.equal('POST')
            // it is a good practice to add assertion messages
            // as the 2nd argument to expect()
            expect(response.statusCode, 'response status').to.eq(200)
          })
      })

    })

    // context('It Creates And Sets Value of Slider Type', () => {
    //   it('Creates Slider Attribute', () => {
    //     cy.get('#open_main_menu > .v-btn__content').click({force:true});
    //     cy.get('[data-cy=main_menu_labels]').click({force:true});
    //     cy.wait(2000)
    //     cy.get(`[data-cy='${labelsForAttributes[1].name}']`).should('exist')
    //     const selectAttribute = labelsForAttributes[1].attributes.filter(attr => attr.type === 'slider')[0];
    //     cy.get(`[data-cy=new_attribute_button]`).click({force: true});
    //     cy.get(`[data-cy="attribute_group_header_Untitled Attribute Group"]`).click({force: true});
    //     cy.get('[data-cy=attribute_kind_select]').click({force: true});
    //     cy.get('.v-list.v-select-list div').contains('Slider').click({force: true})
    //     cy.get('[data-cy=attribute_prompt]').click();
    //     cy.get('[data-cy=attribute_prompt]').type(selectAttribute.prompt);
    //     cy.get('[data-cy=attribute_tag]').click();
    //     cy.get('[data-cy=attribute_tag]').type(selectAttribute.tag);
    //     cy.get('[data-cy=min_value]').click().type('{backspace}{backspace}1')
    //     cy.get('[data-cy=max_value]').click().type('{backspace}{backspace}20')
    //     cy.get('[data-cy=label_select_attribute]').click({force: true});
    //     cy.get('.v-menu__content .v-list.v-select-list div span').contains(labelsForAttributes[0].name).first().click({force: true})
    //     cy.get('[data-cy=attribute_kind_select]').click({force: true});
    //
    //   })

      // it('Sets the value for the slider attribute in the studio', () =>{
      //
      //   const selectAttribute = labelsForAttributes[1].attributes.filter(attr => attr.type === 'slider')[0];
      //   cy.get('#open_main_menu > .v-btn__content').click({force:true});
      //   cy.get('[data-cy="main_menu_data_explorer"]').click({force:true});
      //   cy.wait(2000);
      //   cy.get('[data-cy="minimize-file-explorer-button"] > .v-btn__content').click({force:true});
      //   cy.get('[data-cy="car with Attributes"]').first().click({force:true});
      //
      //   // Draw a box
      //   cy.mousedowncanvas(75, 75);
      //   cy.mouseupcanvas();
      //   cy.mousedowncanvas(120, 120);
      //   cy.mouseupcanvas();
      //
      //   // Select The Attribute
      //   cy.get(`[data-cy="attribute_group_header_${selectAttribute.prompt}"]`).first().click();
      //
      //   //
      //   cy.get(`[data-cy="${selectAttribute.prompt}_value_slider"]`).first().parent().click({force: true}).type('5', {force:true})
      //
      //   // Save The attribute
      //   cy.intercept(`api/project/*/file/*/annotation/update`).as('annotation_update')
      //   cy.get('body').type('{esc}');
      //
      //   cy.get('[data-cy="save_button"]').click({force: true})
      //   cy.wait('@annotation_update')
      //     .should(({request, response}) => {
      //       expect(request.method).to.equal('POST')
      //       // it is a good practice to add assertion messages
      //       // as the 2nd argument to expect()
      //       expect(response.statusCode, 'response status').to.eq(200)
      //     })
      // })

    // })
  })

})
