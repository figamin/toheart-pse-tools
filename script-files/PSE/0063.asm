0:{
text(1)
op_03EC()
op_03F5()
op_0004()
op_0000()
}

1:{
mov(v120,51)
mov(v121,0)
call(57345,1)
dat_call(100,1)
op_0000()
}

2:{
test_seen(3254)
stack_pop(51)
set_seen(3254)
sprite_anim(v6,1,75)
sprite_load(v37,20,75)
dat_call(1568,1)
op_0004()
op_0000()
}

3:{
bg_pos(v51,5,123)
sprite_anim(v8,2,123)
sprite_anim(v6,1,117)
sprite_load(v37,20,117)
dat_call(2072,1)
dat_call(209,1)
sprite_load(v41,18,137)
dat_call(2615,1)
sprite_anim(v6,1,157)
sprite_load(v37,20,157)
bg_load(163)
dat_call(208,1)
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
dat_call(3936,1)
test_seen(3253)
msg_reset()
msg_wait_idle()
msg_sync()
op_0402(30)
op_0410(337,11,10)
text(2)
op_03EA()
op_03E8()
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
set_seen(3253)
op_0004()
op_0000()
}
