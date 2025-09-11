import { RestService } from './restService';
import { Category } from '../models';

export class ListService extends RestService<Category> {
    public constructor(baseUrl: string, baseRoute: string) {
        super(baseUrl, baseRoute);
    }
}
