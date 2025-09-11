import { Dispatch } from "react";
import { Category } from "../models";
import { ListService } from "../services/listService";
import { ActionTypes } from "./common";
import config from "../config"
import { trackEvent } from "../services/telemetryService";
import { ActionMethod, createPayloadAction, PayloadAction } from "./actionCreators";
import { QueryOptions } from "./itemActions";

const listService = new ListService(config.api.baseUrl, '/categories');

export interface ListActions {
    list(options?: QueryOptions): Promise<Category[]>
    load(id: string): Promise<Category>
    select(category: Category): Promise<Category>
    save(category: Category): Promise<Category>
    remove(id: string): Promise<void>
}

export const list = (options?: QueryOptions): ActionMethod<Category[]> => async (dispatch: Dispatch<ListListsAction>) => {
    const categories = await listService.getList(options);

    dispatch(listListsAction(categories));

    return categories;
}

export const select = (category: Category): ActionMethod<Category> => (dispatch: Dispatch<SelectListAction>) => {
    dispatch(selectListAction(category));

    return Promise.resolve(category);
}

export const load = (id: string): ActionMethod<Category> => async (dispatch: Dispatch<LoadListAction>) => {
    const category = await listService.get(id);

    dispatch(loadListAction(category));

    return category;
}

export const save = (category: Category): ActionMethod<Category> => async (dispatch: Dispatch<SaveListAction>) => {
    const newCategory = await listService.save(category);

    dispatch(saveListAction(newCategory));

    trackEvent(ActionTypes.SAVE_TODO_LIST.toString());

    return newCategory;
}

export const remove = (id: string): ActionMethod<void> => async (dispatch: Dispatch<DeleteListAction>) => {
    await listService.delete(id);

    dispatch(deleteListAction(id));
}

export interface ListListsAction extends PayloadAction<string, Category[]> {
    type: ActionTypes.LOAD_TODO_LISTS
}

export interface SelectListAction extends PayloadAction<string, Category | undefined> {
    type: ActionTypes.SELECT_TODO_LIST
}

export interface LoadListAction extends PayloadAction<string, Category> {
    type: ActionTypes.LOAD_TODO_LIST
}

export interface SaveListAction extends PayloadAction<string, Category> {
    type: ActionTypes.SAVE_TODO_LIST
}

export interface DeleteListAction extends PayloadAction<string, string> {
    type: ActionTypes.DELETE_TODO_LIST
}

const listListsAction = createPayloadAction<ListListsAction>(ActionTypes.LOAD_TODO_LISTS);
const selectListAction = createPayloadAction<SelectListAction>(ActionTypes.SELECT_TODO_LIST);
const loadListAction = createPayloadAction<LoadListAction>(ActionTypes.LOAD_TODO_LIST);
const saveListAction = createPayloadAction<SaveListAction>(ActionTypes.SAVE_TODO_LIST);
const deleteListAction = createPayloadAction<DeleteListAction>(ActionTypes.DELETE_TODO_LIST);
