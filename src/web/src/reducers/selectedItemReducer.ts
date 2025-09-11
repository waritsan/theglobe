import { Reducer } from "react";
import { ActionTypes, TodoActions } from "../actions/common";
import { BlogPost } from "../models"

export const selectedItemReducer: Reducer<BlogPost | undefined, TodoActions> = (state: BlogPost | undefined, action: TodoActions): BlogPost | undefined => {
    switch (action.type) {
        case ActionTypes.SELECT_TODO_ITEM:
        case ActionTypes.LOAD_TODO_ITEM:
            state = action.payload ? { ...action.payload } : undefined;
            break;
        case ActionTypes.LOAD_TODO_LIST:
            state = undefined;
            break;
        case ActionTypes.DELETE_TODO_ITEM:
            if (state && state.id === action.payload) {
                state = undefined;
            }
    }

    return state;
}