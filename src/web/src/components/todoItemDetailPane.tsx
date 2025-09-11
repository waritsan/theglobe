import { Text, Stack, FontIcon } from '@fluentui/react';
import { FC, ReactElement } from 'react';
import { stackItemPadding } from '../ux/styles';

interface TodoItemDetailPaneProps {
    item?: any;
    onEdit: (item: any) => void
    onCancel: () => void
}

export const TodoItemDetailPane: FC<TodoItemDetailPaneProps> = (props: TodoItemDetailPaneProps): ReactElement => {
    return (
        <Stack>
            {!props.item &&
                <Stack.Item tokens={stackItemPadding} style={{ textAlign: "center" }} align="center">
                    <FontIcon iconName="WorkItem" style={{ fontSize: 24, padding: 20 }} />
                    <Text block>Select a blog post to edit</Text>
                </Stack.Item>}
        </Stack >
    );
}

export default TodoItemDetailPane;