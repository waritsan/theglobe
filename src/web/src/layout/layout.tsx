import { FC, ReactElement, useContext, useEffect } from 'react';
import Header from './header';
import Sidebar from './sidebar';
import { Routes, Route } from 'react-router-dom';
import HomePage from '../pages/homePage';
import { Stack } from '@fluentui/react';
import { AppContext } from '../models/applicationState';
import { BlogContext } from '../components/todoContext';
import { headerStackStyles, mainStackStyles, rootStackStyles, sidebarStackStyles } from '../ux/styles';
import { Category } from '../models/blogModels';

const Layout: FC = (): ReactElement => {
    const appContext = useContext<AppContext>(BlogContext)

    // Load initial data
    useEffect(() => {
        // TODO: Load blog posts and categories
        console.log('Loading blog data...');
    }, []);

    const onCategoryCreate = (category: Category) => {
        // TODO: Implement category creation
        console.log('Category created:', category);
    }

    return (
        <Stack styles={rootStackStyles}>
            <Stack.Item styles={headerStackStyles}>
                <Header></Header>
            </Stack.Item>
            <Stack horizontal grow={1}>
                <Stack.Item styles={sidebarStackStyles}>
                    <Sidebar
                        selectedCategory={appContext.state.selectedCategory}
                        categories={appContext.state.categories}
                        onCategoryCreate={onCategoryCreate} />
                </Stack.Item>
                <Stack.Item grow={1} styles={mainStackStyles}>
                    <Routes>
                        <Route path="/posts/:postId" element={<HomePage />} />
                        <Route path="/categories/:categoryId" element={<HomePage />} />
                        <Route path="/" element={<HomePage />} />
                    </Routes>
                </Stack.Item>
                <Stack.Item styles={sidebarStackStyles}>
                    {/* TODO: Create blog post detail pane */}
                    <div>Blog Post Detail Pane - Coming Soon</div>
                </Stack.Item>
            </Stack>
        </Stack>
    );
}

export default Layout;
