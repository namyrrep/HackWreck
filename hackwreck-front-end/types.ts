
export interface HackProject {
  id: number;
  name: string;
  framework: string;
  githubLink: string;
  place: string; // 'win' or 'lose'
  topic: string;
  descriptions: string;
  tableNumber?: number;
  ai_score?: number;
}

export interface SearchResponse {
  projects: HackProject[];
  count: number;
}
