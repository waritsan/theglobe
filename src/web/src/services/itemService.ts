import { RestService } from './restService';
import { BlogPost } from '../models';

export class BlogService extends RestService<BlogPost> {
    public constructor(baseUrl: string, baseRoute: string) {
        super(baseUrl, baseRoute);
    }

    // Get published posts only
    async getPublishedPosts(categoryId?: string): Promise<BlogPost[]> {
        const params = new URLSearchParams();
        params.append('published', 'true');
        if (categoryId) {
            params.append('category_id', categoryId);
        }
        // Use getList with query options
        return this.getList();
    }

    // Get posts by category
    async getPostsByCategory(categoryId: string): Promise<BlogPost[]> {
        // For now, get all and filter client-side
        const allPosts = await this.getList();
        return allPosts.filter(post => post.categoryId === categoryId && post.published);
    }

    // Publish/unpublish a post
    async togglePublishStatus(id: string, published: boolean): Promise<BlogPost> {
        return this.patch(id, { published });
    }
}
