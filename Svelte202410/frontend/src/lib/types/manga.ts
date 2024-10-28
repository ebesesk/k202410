export interface Manga {
    id: number;
    folder_name: string;
    tags: string | null;
    page: number;
    images_name: string | null;
    create_date: string;
    update_date: string;
    file_date: string | null;
}
