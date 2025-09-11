import { Dispatch } from "react";
import { TodoActions } from "../actions/common";
import { BlogPost, Category } from "./blogModels";

export interface AppContext {
    state: ApplicationState
    dispatch: Dispatch<TodoActions>
}

export interface ApplicationState {
    categories?: Category[]
    selectedCategory?: Category
    posts?: BlogPost[]
    selectedPost?: BlogPost
}

export const getDefaultState = (): ApplicationState => {
    return {
        categories: undefined,
        selectedCategory: undefined,
        posts: undefined,
        selectedPost: undefined
    }
}

