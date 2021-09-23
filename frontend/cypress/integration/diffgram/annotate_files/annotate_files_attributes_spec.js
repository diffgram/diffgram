import testUser from '../../../fixtures/users.json';
import labelsForAttributes from '../../../fixtures/labelsForAttributes.json';


describe('Annotate Files Tests', () => {

  context('Test Annotate Files Attributes Feature', () => {
    before(function () {
      Cypress.Cookies.debug(true, {verbose: true})
      Cypress.Cookies.defaults({
        preserve: ['session']
      })
      // login before all tests
      cy.loginByForm(testUser.email, testUser.password);
      cy.gotToProject(testUser.project_string_id);
      cy.createLabels(labelsForAttributes)
      cy.uploadAndViewSampleImage(testUser.project_string_id);

    })

    context('It Creates And Sets Value of Select Type', () => {
      it('Creates Select Attribute', () => {
        cy.wait(3000);
        cy.get('#open_main_menu > .v-btn__content').click({force: true});
        cy.get('[data-cy=main_menu_labels]').click({force:true})
        cy.wait(2000)
        cy.get(`[data-cy='${labelsForAttributes[0].name}']`).should('exist')
        const selectAttribute = labelsForAttributes[0].attributes.filter(attr => attr.type === 'select')[0];
        cy.get(`[data-cy=new_attribute_button]`).click({force: true});
        cy.get(`[data-cy="attribute_group_header_Untitled Attribute Group"]`).click({force: true});
        cy.get('[data-cy=attribute_kind_select]').click({force: true});
        cy.get('.v-list.v-select-list div').contains('Select').click({force: true})
        cy.get('[data-cy=attribute_prompt]').click();
        cy.get('[data-cy=attribute_prompt]').type(selectAttribute.prompt);
        cy.get('[data-cy=attribute_tag]').click({force: true});
        cy.get('[data-cy=attribute_tag]').type(selectAttribute.tag);
        cy.get('.v-btn__content > .green--text').click({force: true});

        for(let option of selectAttribute.options){
          cy.get('[data-cy=attribute_option_name]').click({force: true});
          cy.wait(750)
          cy.get('[data-cy=attribute_option_name]').type(option);
          cy.get('[data-cy="create_attribute_option"] > .v-btn__content').click({force: true});

        }
        cy.get('[data-cy="close_button_new_attribute"]').click({force: true});
        cy.get('[data-cy=label_select_attribute]').click({force: true});
        cy.get('.v-menu__content .v-list.v-select-list .v-list-item span span').contains(labelsForAttributes[0].name).first().click({force: true})
        cy.get('[data-cy=attribute_kind_select]').click({force: true});


      })

      it('Sets the value for the select attribute in the studio', () =>{
        cy.wait(3000);
        const selectAttribute = labelsForAttributes[0].attributes.filter(attr => attr.type === 'select')[0];

        cy.get('#open_main_menu > .v-btn__content').click({force: true});
        cy.get('[data-cy="main_menu_data_explorer"]').click({force: true});
        cy.wait(5000);
        cy.get('[data-cy="minimize-file-explorer-button"] > .v-btn__content').click({force: true});
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

    context('It Creates And Sets Value of Free Text Type', () => {
      it('Creates Free Text Attribute', () => {
        cy.wait(3000);
        cy.get('#open_main_menu > .v-btn__content').click({force: true});
        cy.get('[data-cy=main_menu_labels]').click({force:true});
        cy.wait(2000)
        cy.get(`[data-cy='${labelsForAttributes[0].name}']`).should('exist')
        const selectAttribute = labelsForAttributes[0].attributes.filter(attr => attr.type === 'text')[0];
        cy.get(`[data-cy=new_attribute_button]`).click({force: true});
        cy.get(`[data-cy="attribute_group_header_Untitled Attribute Group"]`).click({force: true});
        cy.get('[data-cy=attribute_kind_select]').click({force: true});
        cy.get('.v-list.v-select-list div').contains('Free Text').click({force: true})
        cy.get('[data-cy=attribute_prompt]').click({force: true});
        cy.get('[data-cy=attribute_prompt]').type(selectAttribute.prompt);
        cy.get('[data-cy=attribute_tag]').click({force: true});
        cy.get('[data-cy=attribute_tag]').type(selectAttribute.tag);

        cy.get('[data-cy=label_select_attribute]').click({force: true});
        cy.get('.v-menu__content .v-list.v-select-list div span').contains(labelsForAttributes[0].name).first().click({force: true})
        cy.get('[data-cy=attribute_kind_select]').click({force: true});


      })

      it('Sets the value for the free text attribute in the studio', () =>{
        cy.wait(3000);
        const selectAttribute = labelsForAttributes[0].attributes.filter(attr => attr.type === 'text')[0];
        cy.get('#open_main_menu > .v-btn__content').click({force: true});
        cy.get('[data-cy="main_menu_data_explorer"]').click({force: true});
        cy.wait(2000);
        cy.get('[data-cy="minimize-file-explorer-button"] > .v-btn__content').click({force: true});
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

    context('It Creates And Sets Value of Multiple Select Type', () => {
      it('Creates Free Text Attribute', () => {
        cy.wait(3000);
        cy.get('#open_main_menu > .v-btn__content').click({force: true});
        cy.get('[data-cy=main_menu_labels]').click({force:true});
        cy.wait(2000)
        cy.get(`[data-cy='${labelsForAttributes[0].name}']`).should('exist')
        const selectAttribute = labelsForAttributes[0].attributes.filter(attr => attr.type === 'multiple_select')[0];
        cy.get(`[data-cy=new_attribute_button]`).click({force: true});
        cy.get(`[data-cy="attribute_group_header_Untitled Attribute Group"]`).click({force: true});
        cy.get('[data-cy=attribute_kind_select]').click({force: true});
        cy.get('.v-list.v-select-list div').contains('Multiple Select').click({force: true})
        cy.get('[data-cy=attribute_prompt]').click();
        cy.get('[data-cy=attribute_prompt]').type(selectAttribute.prompt);
        cy.get('[data-cy=attribute_tag]').click();
        cy.get('[data-cy=attribute_tag]').type(selectAttribute.tag);
        cy.get('.v-btn__content > .green--text').click({force: true});
        for(let option of selectAttribute.options){
          cy.get('[data-cy=attribute_option_name]').click({force: true});
          cy.wait(750)
          cy.get('[data-cy=attribute_option_name]').type(option);
          cy.get('[data-cy="create_attribute_option"] > .v-btn__content').click({force: true});

        }
        cy.get('[data-cy="close_button_new_attribute"]').click({force: true});
        cy.get('[data-cy=label_select_attribute]').click({force: true});
        cy.get('.v-menu__content .v-list.v-select-list div span').contains(labelsForAttributes[0].name).first().click({force: true})
        cy.get('[data-cy=attribute_kind_select]').click({force: true});


      })

      it('Sets the value for the multiple select attribute in the studio', () =>{
        cy.wait(3000);
        const selectAttribute = labelsForAttributes[0].attributes.filter(attr => attr.type === 'multiple_select')[0];
        cy.get('#open_main_menu > .v-btn__content').click({force: true});
        cy.get('[data-cy="main_menu_data_explorer"]').click({force: true});
        cy.wait(2000);
        cy.get('[data-cy="minimize-file-explorer-button"] > .v-btn__content').click({force: true});
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
        cy.get(`[data-cy="${selectAttribute.prompt}_value_multiple_select"]`).click({force: true});
        cy.get('.v-menu__content .v-list.v-select-list div').contains(selectAttribute.options[0]).first().click({force: true})
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

    context('It Creates And Sets Value of Radio Button Type', () => {
      it('Creates Radio Button Attribute', () => {
        cy.wait(3000);
        cy.get('#open_main_menu > .v-btn__content').click({force: true});
        cy.get('[data-cy=main_menu_labels]').click({force:true});
        cy.wait(2000)
        cy.get(`[data-cy='${labelsForAttributes[1].name}']`).should('exist')
        const selectAttribute = labelsForAttributes[1].attributes.filter(attr => attr.type === 'radio')[0];
        cy.get(`[data-cy=new_attribute_button]`).click({force: true});
        cy.get(`[data-cy="attribute_group_header_Untitled Attribute Group"]`).click({force: true});
        cy.get('[data-cy=attribute_kind_select]').click({force: true});
        cy.get('.v-list.v-select-list div').contains('Radio Buttons').click({force: true})
        cy.get('[data-cy=attribute_prompt]').click();
        cy.get('[data-cy=attribute_prompt]').type(selectAttribute.prompt);
        cy.get('[data-cy=attribute_tag]').click();
        cy.get('[data-cy=attribute_tag]').type(selectAttribute.tag);
        cy.get('.v-btn__content > .green--text').click({force: true});
        for(let option of selectAttribute.options){
          cy.get('[data-cy=attribute_option_name]').click({force: true});
          cy.wait(750)
          cy.get('[data-cy=attribute_option_name]').type(option);
          cy.get('[data-cy="create_attribute_option"] > .v-btn__content').click({force: true});

        }
        cy.get('[data-cy="close_button_new_attribute"]').click({force: true});
        cy.get('[data-cy=label_select_attribute]').click({force: true});
        cy.get('.v-menu__content .v-list.v-select-list div span').contains(labelsForAttributes[0].name).first().click({force: true})
        cy.get('[data-cy=attribute_kind_select]').click({force: true});

      })

      it('Sets the value for the radio button attribute in the studio', () =>{
        cy.wait(3000);
        const selectAttribute = labelsForAttributes[1].attributes.filter(attr => attr.type === 'radio')[0];
        cy.get('#open_main_menu > .v-btn__content').click({force: true});
        cy.get('[data-cy="main_menu_data_explorer"]').click({force: true});
        cy.wait(2000);
        cy.get('[data-cy="minimize-file-explorer-button"] > .v-btn__content').click({force: true});
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
