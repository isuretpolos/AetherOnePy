/*export class Files {
  folders:FileCategory[] = []
}

export class FileCategory {
  name:string = ""
  files:string[] = []
}*/

export interface FolderStructure {
  folders: {
    [folderName: string]: string[]; // folderName is dynamic, and the value is an array of strings
  };
}
