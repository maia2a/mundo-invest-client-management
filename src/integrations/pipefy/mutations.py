# GraphQL queries matching the official Pipefy GraphQL API schema.
# Docs: https://api.pipefy.com/ (GraphQL reference)

CREATE_CARD_MUTATION = """
mutation CreateCard($input: CreateCardInput!) {
  createCard(input: $input) {
    card {
      id
      title
    }
    clientMutationId
  }
}
"""

UPDATE_CARD_FIELD_MUTATION = """
mutation UpdateCardField($input: UpdateCardFieldInput!) {
  updateCardField(input: $input) {
    card {
      id
    }
    success
    clientMutationId
  }
}
"""

UPDATE_FIELDS_VALUES_MUTATION = """
mutation UpdateFieldsValues($input: UpdateFieldsValuesInput!) {
  updateFieldsValues(input: $input) {
    card {
      id
    }
    success
    clientMutationId
  }
}
"""