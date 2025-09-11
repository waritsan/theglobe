import { Reducer } from "react";
import { ActionTypes, TodoActions } from "../actions/common";
import { Category } from "../models"

export const selectedListReducer: Reducer<Category | undefined, TodoActions> = (state: Category | undefined, action: TodoActions) => {
    switch (action.type) {
        case ActionTypes.SELECT_TODO_LIST:
        case ActionTypes.LOAD_TODO_LIST:
            state = action.payload ? { ...action.payload } : undefined;
            break;
        case ActionTypes.DELETE_TODO_LIST:
            if (state && state.id === action.payload) {
                state = undefined;
            }
            break;
    }

    return state;
}