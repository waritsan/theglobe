import { Stack, Text, FontIcon } from '@fluentui/react';
import { ReactElement, FC } from 'react';
import { stackItemPadding } from '../ux/styles';

interface TodoItemListPaneProps {
    list?: any
    items?: any[]
    selectedItem?: any;
    disabled: boolean
    onCreated: (item: any) => void
    onDelete: (item: any) => void
    onComplete: (item: any) => void
    onSelect: (item?: any) => void
}

const TodoItemListPane: FC<TodoItemListPaneProps> = (): ReactElement => {
    return (
        <Stack>
            <Stack.Item align="center" tokens={stackItemPadding}>
                <FontIcon iconName="ReadingMode" style={{ fontSize: 24, padding: 20 }} />
                <Text>Blog posts will be displayed here</Text>
            </Stack.Item>
        </Stack>
    );
};

export default TodoItemListPane;