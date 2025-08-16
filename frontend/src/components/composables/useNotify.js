import { h, render } from 'vue'

import Notify from '../templates/Notify.vue'

let instance = null

export function useNotify() {
  if (!instance) {
    const mountNode = document.createElement('div')
    document.body.appendChild(mountNode)
    const vnode = h(Notify)
    render(vnode, mountNode)
    instance = vnode.component.exposed
  }

  return {
    show: instance.showNotify
  }
}
