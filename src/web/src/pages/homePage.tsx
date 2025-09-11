import { useEffect, useState, Fragment } from 'react';
import { IconButton, IContextualMenuProps, IIconProps, Stack, Text, Shimmer, ShimmerElementType, PrimaryButton, TextField, Dialog, DialogType, DialogFooter, DefaultButton, Link } from '@fluentui/react';
import { stackItemPadding, stackPadding, titleStackStyles } from '../ux/styles';
import { useNavigate, useParams } from 'react-router-dom';
import WithApplicationInsights from '../components/telemetryWithAppInsights.tsx';

interface BlogPost {
    id: string;
    title: string;
    content: string;
    excerpt?: string;
    author: string;
    categoryId?: string;
    tags?: string[];
    slug: string;
    published: boolean;
    publishedDate?: string;
    createdDate?: string;
    updatedDate?: string;
}

const HomePage = () => {
    const navigate = useNavigate();
    const { postId, categoryId } = useParams();
    const [isReady, setIsReady] = useState(false);
    const [showCreateDialog, setShowCreateDialog] = useState(false);
    const [newPostTitle, setNewPostTitle] = useState('');
    const [newPostContent, setNewPostContent] = useState('');
    const [newPostAuthor, setNewPostAuthor] = useState('Your Name');
    const [posts, setPosts] = useState<BlogPost[]>([]);
    const [loadingPosts, setLoadingPosts] = useState(false);

    // Load initial data
    useEffect(() => {
        const loadData = async () => {
            try {
                console.log('Loading blog posts and categories...');
                await loadPosts();
                setIsReady(true);
            } catch (error) {
                console.error('Error loading blog data:', error);
            }
        };

        loadData();
    }, []);

    // Function to load posts from API
    const loadPosts = async () => {
        setLoadingPosts(true);
        try {
            const response = await fetch('http://localhost:3100/posts');
            if (response.ok) {
                const postsData = await response.json();
                setPosts(postsData);
            } else {
                console.error('Failed to load posts');
            }
        } catch (error) {
            console.error('Error loading posts:', error);
        } finally {
            setLoadingPosts(false);
        }
    };

    // React to category changes
    useEffect(() => {
        if (categoryId) {
            // TODO: Load posts for selected category
            console.log('Loading posts for category:', categoryId);
        }
    }, [categoryId]);

    // React to post selection
    useEffect(() => {
        if (postId) {
            // TODO: Load selected post details
            console.log('Loading post details:', postId);
        }
    }, [postId]);

    const createPost = async () => {
        if (!newPostTitle.trim() || !newPostContent.trim()) {
            alert('Please fill in both title and content');
            return;
        }

        try {
            const response = await fetch('http://localhost:3100/posts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: newPostTitle,
                    content: newPostContent,
                    author: newPostAuthor,
                    slug: newPostTitle.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, ''),
                    published: true
                })
            });

            if (response.ok) {
                alert('Blog post created successfully!');
                setShowCreateDialog(false);
                setNewPostTitle('');
                setNewPostContent('');
                // Refresh the posts list
                await loadPosts();
            } else {
                alert('Failed to create blog post');
            }
        } catch (error) {
            console.error('Error creating post:', error);
            alert('Error creating blog post');
        }
    };

    const deleteCategory = () => {
        if (categoryId) {
            // TODO: Implement category deletion
            console.log('Deleting category:', categoryId);
            navigate('/');
        }
    }

    const iconProps: IIconProps = {
        iconName: 'More',
        styles: {
            root: {
                fontSize: 14
            }
        }
    }

    const menuProps: IContextualMenuProps = {
        items: [
            {
                key: 'create',
                text: 'Create Post',
                iconProps: { iconName: 'Add' },
                onClick: () => { setShowCreateDialog(true) }
            },
            {
                key: 'delete',
                text: 'Delete Category',
                iconProps: { iconName: 'Delete' },
                onClick: () => { deleteCategory() }
            }
        ]
    }

    return (
        <Stack>
            <Stack.Item>
                <Stack horizontal styles={titleStackStyles} tokens={stackPadding}>
                    <Stack.Item grow={1}>
                        <Shimmer width={300}
                            isDataLoaded={isReady}
                            shimmerElements={
                                [
                                    { type: ShimmerElementType.line, height: 20 }
                                ]
                            } >
                            <Fragment>
                                <Text block variant="xLarge">Blog Posts</Text>
                                <Text variant="small">Manage your blog content</Text>
                            </Fragment>
                        </Shimmer>
                    </Stack.Item>
                    <Stack.Item>
                        <IconButton
                            disabled={!isReady}
                            menuProps={menuProps}
                            iconProps={iconProps}
                            styles={{ root: { fontSize: 16 } }}
                            title="Blog Actions"
                            ariaLabel="Blog Actions" />
                    </Stack.Item>
                </Stack>
            </Stack.Item>
            <Stack.Item tokens={stackItemPadding}>
                <div>
                    <h3>Blog Posts</h3>
                    {loadingPosts ? (
                        <Text>Loading posts...</Text>
                    ) : posts.length === 0 ? (
                        <div>
                            <p>No posts found. Create your first blog post!</p>
                            <PrimaryButton
                                text="Create New Post"
                                iconProps={{ iconName: 'Add' }}
                                onClick={() => setShowCreateDialog(true)}
                                styles={{ root: { marginTop: 16 } }}
                            />
                        </div>
                    ) : (
                        <div>
                            <PrimaryButton
                                text="Create New Post"
                                iconProps={{ iconName: 'Add' }}
                                onClick={() => setShowCreateDialog(true)}
                                styles={{ root: { marginBottom: 16 } }}
                            />
                            <Stack tokens={{ childrenGap: 16 }}>
                                {posts.map((post) => (
                                    <Stack
                                        key={post.id}
                                        styles={{
                                            root: {
                                                padding: 16,
                                                border: '1px solid #e1e1e1',
                                                borderRadius: 4,
                                                backgroundColor: '#fafafa'
                                            }
                                        }}
                                    >
                                        <Text block variant="large" styles={{ root: { fontWeight: 600 } }}>
                                            {post.title}
                                        </Text>
                                        <Text variant="small" styles={{ root: { color: '#666' } }}>
                                            By {post.author} on {new Date(post.createdDate || '').toLocaleDateString()}
                                            {post.tags && post.tags.length > 0 && (
                                                <span> • Tags: {post.tags.join(', ')}</span>
                                            )}
                                        </Text>
                                        <Text block styles={{ root: { marginTop: 8, lineHeight: 1.5 } }}>
                                            {post.excerpt || post.content.substring(0, 200) + (post.content.length > 200 ? '...' : '')}
                                        </Text>
                                        <Stack horizontal tokens={{ childrenGap: 8 }} styles={{ root: { marginTop: 12 } }}>
                                            <Link
                                                href={`/posts/${post.id}`}
                                                styles={{ root: { fontSize: 14 } }}
                                            >
                                                Read More
                                            </Link>
                                            {!post.published && (
                                                <Text variant="small" styles={{ root: { color: '#d13438', fontStyle: 'italic' } }}>
                                                    Draft
                                                </Text>
                                            )}
                                        </Stack>
                                    </Stack>
                                ))}
                            </Stack>
                        </div>
                    )}
                </div>
            </Stack.Item>

            <Dialog
                hidden={!showCreateDialog}
                onDismiss={() => setShowCreateDialog(false)}
                dialogContentProps={{
                    type: DialogType.normal,
                    title: 'Create New Blog Post',
                    subText: 'Fill in the details for your new blog post.'
                }}
                modalProps={{
                    isBlocking: false,
                    styles: { main: { maxWidth: 450 } }
                }}
            >
                <Stack tokens={{ childrenGap: 12 }}>
                    <TextField
                        label="Title"
                        placeholder="Enter blog post title"
                        value={newPostTitle}
                        onChange={(_, value) => setNewPostTitle(value || '')}
                        required
                    />
                    <TextField
                        label="Author"
                        placeholder="Your name"
                        value={newPostAuthor}
                        onChange={(_, value) => setNewPostAuthor(value || '')}
                    />
                    <TextField
                        label="Content"
                        placeholder="Write your blog post content here..."
                        multiline
                        rows={6}
                        value={newPostContent}
                        onChange={(_, value) => setNewPostContent(value || '')}
                        required
                    />
                </Stack>
                <DialogFooter>
                    <PrimaryButton onClick={createPost} text="Create Post" />
                    <DefaultButton onClick={() => setShowCreateDialog(false)} text="Cancel" />
                </DialogFooter>
            </Dialog>
        </Stack >
    );
};

const HomePageWithTelemetry = WithApplicationInsights(HomePage, 'HomePage');

export default HomePageWithTelemetry;
