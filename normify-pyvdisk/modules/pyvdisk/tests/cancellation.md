---
uid: a0000e1c
id: pyvdisk.tests.cancellation
parent: pyvdisk.tests
name: {zh: "取消用例", en: "Cancellation Tests"}
description:
  zh: >
      验证协作式取消会让队列与运行状态保持一致，不停留在中间状态。
      
  en: >
      Verifies cooperative cancellation leaves the queue and run state consistent, not stuck in a transient status.
      
revision: 6d203c0d5f54ce2e4293edd8054c10a109f8b83d
updated_at: "2026-09-23T07:19:13.025Z"
fingerprint: 9695cdadf64ad0f3f33e7a0b64ac2a10ae7d63faf258a1ae039e0ec99448f736
source:
  - path: "tests/test_worker_cancellation.py"
apis:
  - protocol: rpc
    path: "tests/test_worker_cancellation.py"
    description:
      zh: >
          任务运行中的 worker 取消。
          
      en: >
          Worker cancellation during a running task.
          
deps:
  - kind: call
    to: pyvdisk.execution.service.submit
    to_api: "rpc:pyvdisk.execution.ExecutionService#cancel"
    label: {zh: "验证取消", en: "verifies cancellation"}
---
