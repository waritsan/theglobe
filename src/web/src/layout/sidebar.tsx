import { FC, ReactElement } from 'react';
import BlogCategoryMenu from '../components/todoListMenu';
import { Category } from '../models/blogModels';

interface SidebarProps {
    selectedCategory?: Category
    categories?: Category[];
    onCategoryCreate: (category: Category) => void
}

const Sidebar: FC<SidebarProps> = (props: SidebarProps): ReactElement => {
    return (
        <div>
            <BlogCategoryMenu
                selectedCategory={props.selectedCategory}
                categories={props.categories}
                onCreate={props.onCategoryCreate} />
        </div>
    );
};

export default Sidebar;