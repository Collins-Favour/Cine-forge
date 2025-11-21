import { useQuery } from 'react-query'
import { projectService } from '@services'

export function useProjects() {
  return useQuery('projects', projectService.getAll)
}

export function useProject(id) {
  return useQuery(['project', id], () => projectService.getById(id), {
    enabled: !!id,
  })
}

export function useProjectCollaborators(id) {
  return useQuery(['project-collaborators', id], () => projectService.getCollaborators(id), {
    enabled: !!id,
  })
}
