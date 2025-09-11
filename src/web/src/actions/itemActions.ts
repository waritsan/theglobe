import { Dispatch } from "react";
import { BlogPost } from "../models";
import { BlogService } from "../services/itemService";
import { ActionTypes } from "./common";
import config from "../config"
import { ActionMethod, createPayloadAction, PayloadAction } from "./actionCreators";

export interface QueryOptions {
    [key: string]: RegExp | boolean
}

export interface ItemActions {
    list(options?: QueryOptions): Promise<BlogPost[]>
    select(post?: BlogPost): Promise<BlogPost>
    load(id: string): Promise<BlogPost>
    save(post: BlogPost): Promise<BlogPost>
    remove(post: BlogPost): Promise<void>
    togglePublish(post: BlogPost): Promise<BlogPost>
}

export const list = (): ActionMethod<BlogPost[]> => async (dispatch: Dispatch<ListItemsAction>) => {
    const blogService = new BlogService(config.api.baseUrl, `/posts`);
    const posts = await blogService.getPublishedPosts();

    dispatch(listItemsAction(posts));

    return posts;
}

export const select = (post?: BlogPost): ActionMethod<BlogPost | undefined> => async (dispatch: Dispatch<SelectItemAction>) => {
    dispatch(selectItemAction(post));

    return Promise.resolve(post);
}

export const load = (id: string): ActionMethod<BlogPost> => async (dispatch: Dispatch<LoadItemAction>) => {
    const blogService = new BlogService(config.api.baseUrl, `/posts`);
    const post = await blogService.get(id);

    dispatch(loadItemAction(post));

    return post;
}

export const save = (post: BlogPost): ActionMethod<BlogPost> => async (dispatch: Dispatch<SaveItemAction>) => {
    const blogService = new BlogService(config.api.baseUrl, `/posts`);
    const newPost = await blogService.save(post);

    dispatch(saveItemAction(newPost));

    return newPost;
}

export const remove = (post: BlogPost): ActionMethod<void> => async (dispatch: Dispatch<DeleteItemAction>) => {
    const blogService = new BlogService(config.api.baseUrl, `/posts`);
    if (post.id) {
        await blogService.delete(post.id);
        dispatch(deleteItemAction(post.id));
    }
}

export const togglePublish = (post: BlogPost): ActionMethod<BlogPost> => async (dispatch: Dispatch<TogglePublishAction>) => {
    const blogService = new BlogService(config.api.baseUrl, `/posts`);
    const updatedPost = await blogService.togglePublishStatus(post.id!, !post.published);

    dispatch(togglePublishAction(updatedPost));

    return updatedPost;
}

export interface ListItemsAction extends PayloadAction<string, BlogPost[]> {
    type: ActionTypes.LOAD_TODO_ITEMS
}

export interface SelectItemAction extends PayloadAction<string, BlogPost | undefined> {
    type: ActionTypes.SELECT_TODO_ITEM
}

export interface LoadItemAction extends PayloadAction<string, BlogPost> {
    type: ActionTypes.LOAD_TODO_ITEM
}

export interface SaveItemAction extends PayloadAction<string, BlogPost> {
    type: ActionTypes.SAVE_TODO_ITEM
}

export interface DeleteItemAction extends PayloadAction<string, string> {
    type: ActionTypes.DELETE_TODO_ITEM
}

export interface TogglePublishAction extends PayloadAction<string, BlogPost> {
    type: ActionTypes.TOGGLE_PUBLISH
}

const listItemsAction = createPayloadAction<ListItemsAction>(ActionTypes.LOAD_TODO_ITEMS);
const selectItemAction = createPayloadAction<SelectItemAction>(ActionTypes.SELECT_TODO_ITEM);
const loadItemAction = createPayloadAction<LoadItemAction>(ActionTypes.LOAD_TODO_ITEM);
const saveItemAction = createPayloadAction<SaveItemAction>(ActionTypes.SAVE_TODO_ITEM);
const deleteItemAction = createPayloadAction<DeleteItemAction>(ActionTypes.DELETE_TODO_ITEM);
const togglePublishAction = createPayloadAction<TogglePublishAction>(ActionTypes.TOGGLE_PUBLISH);
