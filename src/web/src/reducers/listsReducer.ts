import { Reducer } from "react";
import { ActionTypes, TodoActions } from "../actions/common";
import { Category } from "../models"

export const listsReducer: Reducer<Category[], TodoActions> = (state: Category[], action: TodoActions): Category[] => {
    switch (action.type) {
        case ActionTypes.LOAD_TODO_LISTS:
            state = [...action.payload];
            break;
        case ActionTypes.SAVE_TODO_LIST:
            state = [...state, action.payload];
            break;
        case ActionTypes.DELETE_TODO_LIST:
            state = [...state.filter(category => category.id !== action.payload)]
    }

    return state;
}