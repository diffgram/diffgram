import testUser from '../../../fixtures/users.json';
import testLabels from '../../../fixtures/labels.json';

const shapes = [
  { type: 'Box', points: [75, 75, 120, 120] },
  { type: 'Polygon', points: [200, 25, 200, 60, 180, 40, 160, 10, 200, 25] },
  { type: 'Line', points: [145, 145, 220, 90] },
  { type: 'Point', points: [25, 25] },
  { type: 'Cuboid', points: [160, 160, 195, 180, 215, 230] },
  { type: 'Ellipse', points: [80, 175, 135, 160] },
];

describe('Annotate Files Tests', () => {
  before(function () {
    Cypress.Cookies.debug(true, {verbose: true})

    cy.loginByForm(testUser.email, testUser.password)
      .gotToProject(testUser.project_string_id)
      .createLabels(testLabels)
      .uploadAndViewSampleImage(testUser.project_string_id)
      .wait(3000)
      .get('[data-cy="minimize-file-explorer-button"]').click({force: true})
      .select_label();
  });

  context('Undo/Redo All Instance Type Creations', () => {
    shapes.forEach((shape) => {
      it(`Correctly Undos a ${shape.type} Creation`, () => {
        createShape(shape);
        undoCreation();
      });
    });
  });

  context('Undo all instance type editions', () => {
    shapes.forEach((shape) => {
      it(`Correctly Undos a ${shape.type} Edition`, () => {
        editShape(shape);
        undoEdition();
      });
    });
  });
});

function createShape(shape) {
  cy.get('[data-cy="instance-type-select"]').click({force: true});
  cy.get('.v-list.v-select-list div').contains(shape.type).click({force: true});
  shape.points.forEach((point, index) => {
    if (index % 2 === 0) {
      cy.mousedowncanvas(point, shape.points[index + 1]);
    } else {
      cy.mouseupcanvas();
    }
  });
  cy.wait(1000);
}

function editShape(shape) {
  cy.get('[data-cy="edit_toggle"]').click({force: true});
  createShape(shape);
}

function undoCreation() {
  cy.get('body').type('{ctrl+z}');
}

function undoEdition() {
  cy.get('body').type('{ctrl+z}');
}
