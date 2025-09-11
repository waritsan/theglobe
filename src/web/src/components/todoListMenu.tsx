import { IIconProps, INavLink, INavLinkGroup, Nav, Stack, TextField } from '@fluentui/react';
import { FC, ReactElement, useState, FormEvent, MouseEvent } from 'react';
import { useNavigate } from 'react-router';
import { Category } from '../models/blogModels';
import { stackItemPadding } from '../ux/styles';

interface BlogCategoryMenuProps {
    selectedCategory?: Category
    categories?: Category[]
    onCreate: (category: Category) => void
}

const iconProps: IIconProps = {
    iconName: 'AddToShoppingList'
}

const BlogCategoryMenu: FC<BlogCategoryMenuProps> = (props: BlogCategoryMenuProps): ReactElement => {
    const navigate = useNavigate();
    const [newCategoryName, setNewCategoryName] = useState('');

    const onNavLinkClick = (evt?: MouseEvent<HTMLElement>, item?: INavLink) => {
        evt?.preventDefault();

        if (!item) {
            return;
        }

        navigate(`/categories/${item.key}`);
    }

    const createNavGroups = (categories: Category[]): INavLinkGroup[] => {
        const links = categories.map(category => ({
            key: category.id || '',
            name: category.name,
            url: `/categories/${category.id}`,
            links: [],
            isExpanded: props.selectedCategory ? category.id === props.selectedCategory.id : false
        }));

        return [{
            links: links
        }]
    }

    const onNewCategoryNameChange = (_evt: FormEvent<HTMLInputElement | HTMLTextAreaElement>, value?: string) => {
        setNewCategoryName(value || '');
    }

    const onFormSubmit = async (evt: FormEvent<HTMLFormElement>) => {
        evt.preventDefault();

        if (newCategoryName) {
            const category: Category = {
                name: newCategoryName,
                slug: newCategoryName.toLowerCase().replace(/\s+/g, '-')
            };

            props.onCreate(category);
            setNewCategoryName('');
        }
    }

    return (
        <Stack>
            <Stack.Item>
                <Nav
                    selectedKey={props.selectedCategory?.id}
                    onLinkClick={onNavLinkClick}
                    groups={createNavGroups(props.categories || [])} />
            </Stack.Item>
            <Stack.Item tokens={stackItemPadding}>
                <form onSubmit={onFormSubmit}>
                    <TextField
                        borderless
                        iconProps={iconProps}
                        value={newCategoryName}
                        disabled={props.selectedCategory == null}
                        placeholder="New Category"
                        onChange={onNewCategoryNameChange} />
                </form>
            </Stack.Item>
        </Stack>
    );
};

export default BlogCategoryMenu;