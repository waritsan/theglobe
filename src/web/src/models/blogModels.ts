export interface BlogPost {
    id?: string
    title: string
    content: string
    excerpt?: string
    author: string
    categoryId?: string
    tags?: string[]
    slug: string
    published: boolean
    publishedDate?: Date
    createdDate?: Date
    updatedDate?: Date
}

export interface Category {
    id?: string
    name: string
    description?: string
    slug: string
    createdDate?: Date
    updatedDate?: Date
}

export interface Comment {
    id?: string
    postId: string
    author: string
    email?: string
    content: string
    approved: boolean
    createdDate?: Date
    updatedDate?: Date
}