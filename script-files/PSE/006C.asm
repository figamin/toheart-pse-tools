0:{
text(1)
op_03E8()
text(2)
op_03EC()
op_03F5()
op_0004()
op_0000()
}

1:{
mov(v120,60)
mov(v121,2)
cmp_eq(v1,3)
call(57345,1)
dat_call(109,1)
op_0000()
}

2:{
bg_pos(v44,11,82)
sprite_load(v32,70,82)
sprite_anim(v1,4,82)
dat_call(336,1)
sprite_anim(v5,1,94)
bg_load(120)
sprite_load(v33,36,114)
sprite_anim(v2,0,114)
bg_load(120)
dat_call(212,1)
test_seen(3313)
stack_pop(60)
set_seen(3313)
op_0004()
op_0000()
}

3:{
sprite_anim(v5,1,150)
dat_call(1302,1)
sprite_load(v33,36,186)
sprite_anim(v2,0,186)
mov(v129,0)
call(584,1)
bg_pos(v129,0,206)
bg_pos(v23,255,200)
dat_call(232,1)
dat_call(229,1)
op_0004()
op_0000()
}

4:{
op_0004()
op_0000()
}

5:{
op_0004()
op_0000()
}

6:{
op_0004()
op_0000()
}

7:{
op_0004()
op_0000()
}

8:{
op_0004()
op_0000()
}

9:{
op_0004()
op_0000()
}

10:{
op_0004()
op_0000()
}

11:{
sprite_load(v41,30,252)
dat_call(2627,1)
test_seen(3323)
msg_reset()
msg_wait_idle()
msg_sync()
op_0402(30)
op_0410(337,11,10)
text(3)
op_03EA()
op_03E8()
text(4)
op_03EC()
op_0412(0,0,11)
msg_reset()
msg_wait_idle()
msg_sync()
op_03F5()
set_seen(3323)
op_0004()
op_0000()
}
